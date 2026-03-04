import csv
import re
from collections import Counter
from datetime import date, datetime, timedelta

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QStyle,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from src.infrastructure.timezone_utils import BERLIN, parse_utc_timestamp
from src.infrastructure.runtime_paths import booking_csv_files
from src.domain.exceptions import DomainException
from src.services.compensation_service import CompensationService


APP_TITLE = "OpsGenie vs. Buchungen vergleichen"
SHIFT_BOUNDARY_HOUR = 1
SHIFT_ORDER = ["F", "T", "S"]
MATCH_BG = QColor("#dbeafe")
MISMATCH_BG = QColor("#ffedd5")
UNKNOWN_EXPECTED_TASK = "__UNKNOWN_EXPECTED_TASK__"


class ShiftBookingCompareDialog(QDialog):
    def __init__(self, p_application, p_parent=None):
        super().__init__(p_parent)
        self._application = p_application
        self._entries: list[dict[str, str | int | None]] = []
        self._compensation_service = CompensationService()
        self._analyst_locations_by_name: dict[str, str] = {}
        self._ok_icon = self.style().standardIcon(QStyle.SP_DialogApplyButton)
        self._mismatch_icon = self.style().standardIcon(QStyle.SP_MessageBoxWarning)
        self._setup_ui()
        self._load_analyst_filter()
        self._load_analyst_locations()
        self._load_schedule_references()

    def _setup_ui(self):
        self.setWindowTitle(APP_TITLE)
        self.resize(1200, 650)

        layout = QVBoxLayout()
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)

        self._schedule_combo = QComboBox()
        self._schedule_combo.currentIndexChanged.connect(self._on_schedule_changed)
        form.addRow("Schichtplan:", self._schedule_combo)

        today = datetime.now(BERLIN).date()
        iso_year, iso_week, _ = today.isocalendar()

        self._week_year_spin = QSpinBox()
        self._week_year_spin.setRange(2000, 2100)
        self._week_year_spin.setValue(iso_year)
        self._week_year_spin.valueChanged.connect(self._on_week_year_changed)
        form.addRow("Jahr:", self._week_year_spin)

        self._calendar_week_spin = QSpinBox()
        self._calendar_week_spin.setRange(1, 53)
        self._calendar_week_spin.setValue(iso_week)
        self._calendar_week_spin.valueChanged.connect(self._render_comparison)
        form.addRow("Kalenderwoche:", self._calendar_week_spin)
        self._sync_week_limits()

        self._analyst_combo = QComboBox()
        self._analyst_combo.currentIndexChanged.connect(self._render_comparison)
        form.addRow("Incident Analyst:", self._analyst_combo)

        layout.addLayout(form)

        tables = QHBoxLayout()

        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Schichtplan (OpsGenie)"))
        self._planned_table = QTableWidget()
        self._planned_table.setColumnCount(4)
        self._planned_table.setHorizontalHeaderLabels(["Datum", "Früh", "Tag", "Spät"])
        self._planned_table.setEditTriggers(QTableWidget.NoEditTriggers)
        left_layout.addWidget(self._planned_table)

        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Gebuchte Schichten"))
        self._booked_table = QTableWidget()
        self._booked_table.setColumnCount(4)
        self._booked_table.setHorizontalHeaderLabels(["Datum", "Früh", "Tag", "Spät"])
        self._booked_table.setEditTriggers(QTableWidget.NoEditTriggers)
        right_layout.addWidget(self._booked_table)

        tables.addLayout(left_layout)
        tables.addLayout(right_layout)
        layout.addLayout(tables)

        action_row = QHBoxLayout()
        action_row.addStretch()
        self._close_button = QPushButton("Dialog schließen")
        self._close_button.clicked.connect(self.close)
        action_row.addWidget(self._close_button)
        layout.addLayout(action_row)

        self.setLayout(layout)

    def _load_schedule_references(self):
        self._schedule_combo.clear()
        refs = self._application.get_schedule_references()
        for ref in refs:
            schedule_name = ref.get("schedule_name", "")
            schedule_id = ref.get("schedule_id", "")
            label = f"{schedule_name} ({schedule_id})" if schedule_name else schedule_id
            self._schedule_combo.addItem(label, ref)

        if not refs:
            QMessageBox.information(self, APP_TITLE, "Keine Schichtplan-Referenzen vorhanden.")
            return
        self._schedule_combo.setCurrentIndex(0)

    def _load_analyst_filter(self):
        self._analyst_combo.clear()
        self._analyst_combo.addItem("Alle", "__all__")
        analysts = self._application.get_all_incident_analysts()
        for analyst in analysts:
            if not analyst.is_active:
                continue
            label = analyst.buchungsname
            self._analyst_combo.addItem(label, label)
        self._analyst_combo.setCurrentIndex(0)

    def _load_analyst_locations(self):
        self._analyst_locations_by_name.clear()
        for analyst in self._application.get_all_incident_analysts():
            if not analyst.is_active:
                continue
            normalized = self._normalize_person_name(str(analyst.buchungsname))
            self._analyst_locations_by_name[normalized] = str(analyst.oncall_location_id).strip().upper()

    def _on_schedule_changed(self, p_index: int):
        if p_index < 0:
            return
        ref = self._schedule_combo.itemData(p_index)
        if not ref:
            return
        schedule_id = ref.get("schedule_id", "")
        self._entries = self._application.get_schedule_entries(schedule_id)
        self._render_comparison()

    def _on_week_year_changed(self):
        self._sync_week_limits()
        self._render_comparison()

    def _sync_week_limits(self):
        year = int(self._week_year_spin.value())
        max_week = date(year, 12, 28).isocalendar().week
        self._calendar_week_spin.setMaximum(max_week)
        if self._calendar_week_spin.value() > max_week:
            self._calendar_week_spin.setValue(max_week)

    def _entry_key(self, p_entry: dict[str, str | int | None]) -> tuple[date, str]:
        start_local = parse_utc_timestamp(str(p_entry["start_time"])).astimezone(BERLIN)
        display_day = start_local.date()
        if start_local.hour < SHIFT_BOUNDARY_HOUR:
            display_day = display_day - timedelta(days=1)

        shifted_hour = (start_local.hour - SHIFT_BOUNDARY_HOUR) % 24
        if shifted_hour < 8:
            slot = "F"
        elif shifted_hour < 16:
            slot = "T"
        else:
            slot = "S"
        return display_day, slot

    def _parse_slot_from_notes(self, p_notes: str) -> str | None:
        normalized = (
            p_notes.strip()
            .lower()
            .replace("[", "")
            .replace("]", "")
            .replace("ä", "ae")
            .replace("ö", "oe")
            .replace("ü", "ue")
            .replace("ß", "ss")
        )
        if "frueh" in normalized or "fruh" in normalized or "early" in normalized:
            return "F"
        if "tag" in normalized or "day" in normalized:
            return "T"
        if "spaet" in normalized or "spat" in normalized or "late" in normalized:
            return "S"
        return None

    def _load_bookings_for_week(
        self,
        p_week_start: date,
        p_week_end: date,
    ) -> dict[tuple[date, str], list[dict[str, str | int | bool | None]]]:
        result: dict[tuple[date, str], list[dict[str, str | int | bool | None]]] = {}
        for file_path in booking_csv_files():
            with file_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
                reader = csv.reader(csv_file, delimiter=";")
                header = None
                for row in reader:
                    if not row:
                        continue
                    if "Task - Task type" in row:
                        header = row
                        break
                if header is None:
                    continue

                index_map = {name: idx for idx, name in enumerate(header)}
                required = ["Date", "User", "Task - Task type", "Notes", "Time (Hours)"]
                if any(key not in index_map for key in required):
                    continue
                task_name_index = self._find_task_name_column(header)
                aggregated: dict[tuple[date, str, str, str], dict[str, str | int | bool | None]] = {}

                for row in reader:
                    if len(row) < len(header):
                        continue
                    task_type = row[index_map["Task - Task type"]].strip().lower()
                    if task_type != "on call":
                        continue

                    try:
                        booking_date = datetime.strptime(
                            row[index_map["Date"]].strip(),
                            "%d-%m-%y",
                        ).date()
                    except ValueError:
                        continue

                    if booking_date < p_week_start or booking_date > p_week_end:
                        continue

                    slot = self._parse_slot_from_notes(row[index_map["Notes"]])
                    if slot is None:
                        continue

                    units = self._compensation_service.parse_booking_units(
                        row[index_map["Time (Hours)"]]
                    )
                    if units is None or units == 0:
                        continue

                    user = row[index_map["User"]].strip()
                    task_name: str | None = None
                    if task_name_index is not None and task_name_index < len(row):
                        task_name = row[task_name_index].strip()
                    expected_task = self._expected_task_for_user_slot(user, booking_date, slot)
                    task_matches = self._task_matches_expected(task_name, expected_task)
                    aggregate_key = (
                        booking_date,
                        slot,
                        user,
                        (task_name or "").casefold(),
                    )
                    entry = aggregated.setdefault(
                        aggregate_key,
                        {
                            "user": user,
                            "task_name": task_name,
                            "expected_task": expected_task,
                            "task_matches": task_matches,
                            "units": 0,
                        },
                    )
                    entry["units"] = int(entry["units"]) + int(units)

                for (booking_date, slot, _user, _task), entry in aggregated.items():
                    units = int(entry.get("units") or 0)
                    if units <= 0:
                        continue
                    net_entry = dict(entry)
                    net_entry["units"] = units
                    key = (booking_date, slot)
                    result.setdefault(key, []).append(net_entry)
        return result

    def _find_task_name_column(self, p_header: list[str]) -> int | None:
        normalized = {
            name.strip().casefold(): idx
            for idx, name in enumerate(p_header)
        }
        candidates = [
            "task",
            "task - task",
            "task - name",
            "task - task name",
            "task name",
        ]
        for candidate in candidates:
            if candidate in normalized:
                return normalized[candidate]
        return None

    def _normalize_task_name(self, p_name: str) -> str:
        collapsed = " ".join(p_name.strip().casefold().split())
        return collapsed

    def _expected_task_for_user_slot(self, p_user: str, p_day: date, p_slot: str) -> str | None:
        normalized_user = self._normalize_person_name(p_user)
        location_id = self._analyst_locations_by_name.get(normalized_user)
        if not location_id:
            return UNKNOWN_EXPECTED_TASK
        try:
            return self._compensation_service.determine_expected_booking_task(
                p_oncall_location_id=location_id,
                p_day=p_day,
                p_slot=p_slot,
            )
        except DomainException:
            return UNKNOWN_EXPECTED_TASK

    def _task_matches_expected(self, p_task_name: str | None, p_expected_task: str | None) -> bool | None:
        if p_expected_task == UNKNOWN_EXPECTED_TASK:
            return None
        if p_task_name is None:
            return None
        if p_expected_task is None:
            if p_task_name.strip():
                return False
            return False
        if not p_task_name.strip():
            return False
        return self._normalize_task_name(p_task_name) == self._normalize_task_name(p_expected_task)

    def _build_booked_counter(
        self,
        p_bookings: list[dict[str, str | int | bool | None]],
    ) -> Counter[str]:
        names: Counter[str] = Counter()
        for entry in p_bookings:
            user = str(entry.get("user") or "").strip()
            if not user:
                continue
            units = int(entry.get("units") or 0)
            if units <= 0:
                continue
            names[user] += units
        return names

    def _mismatch_reasons(
        self,
        p_planned_names: Counter[str],
        p_booked_names: Counter[str],
        p_bookings: list[dict[str, str | int | bool | None]],
        p_day: date,
        p_slot: str,
    ) -> list[str]:
        reasons: list[str] = []
        planned_names_compare = self._normalized_counter(p_planned_names)
        booked_names_compare = self._normalized_counter(p_booked_names)
        is_weekday_day_shift_without_booking = (
            p_slot == "T"
            and p_day.weekday() < 5
            and not p_booked_names
        )

        if planned_names_compare != booked_names_compare and not is_weekday_day_shift_without_booking:
            reasons.append("IA/Anzahl weicht vom Schichtplan ab")

        disallowed_bookings = 0
        wrong_task = 0
        missing_task = 0
        for entry in p_bookings:
            expected_task = entry.get("expected_task")
            task_raw = entry.get("task_name")
            task_name = str(task_raw).strip() if task_raw is not None else ""
            task_matches = entry.get("task_matches")
            if task_matches is not False:
                continue
            if expected_task is None:
                disallowed_bookings += 1
            elif not task_name:
                missing_task += 1
            else:
                wrong_task += 1

        if disallowed_bookings > 0:
            reasons.append("Buchung nicht erlaubt (kein Task erwartet)")
        if wrong_task > 0:
            reasons.append("Falscher Task gewählt")
        if missing_task > 0:
            reasons.append("Taskname fehlt in Buchung")
        return reasons

    def _format_counter_names(self, p_counter: Counter[str], p_empty: str = "") -> str:
        if not p_counter:
            return p_empty
        values: list[str] = []
        for name in sorted(p_counter.keys()):
            count = p_counter[name]
            if count > 1:
                values.append(f"{name} (x{count})")
            else:
                values.append(name)
        return ", ".join(values)

    def _normalize_person_name(self, p_name: str) -> str:
        cleaned = re.sub(r"[^\w\s]", " ", p_name.casefold())
        tokens = [token for token in cleaned.split() if token]
        # Reihenfolge-unabhängige Normalisierung:
        # "Mehta Riten" == "Riten, Mehta"
        return " ".join(sorted(tokens))

    def _normalized_counter(self, p_counter: Counter[str]) -> Counter[str]:
        normalized: Counter[str] = Counter()
        for name, count in p_counter.items():
            normalized[self._normalize_person_name(name)] += count
        return normalized

    def _selected_analyst_normalized(self) -> str | None:
        selected = self._analyst_combo.currentData()
        if selected in (None, "__all__"):
            return None
        return self._normalize_person_name(str(selected))

    def _render_comparison(self):
        year = int(self._week_year_spin.value())
        week = int(self._calendar_week_spin.value())
        week_start = date.fromisocalendar(year, week, 1)
        week_end = week_start + timedelta(days=6)
        selected_analyst = self._selected_analyst_normalized()

        planned: dict[tuple[date, str], Counter[str]] = {}
        for entry in self._entries:
            day, slot = self._entry_key(entry)
            if day < week_start or day > week_end:
                continue
            name = str(entry.get("buchungsname") or "-")
            if selected_analyst is not None:
                if self._normalize_person_name(name) != selected_analyst:
                    continue
            planned.setdefault((day, slot), Counter())[name] += 1

        booked = self._load_bookings_for_week(week_start, week_end)
        if selected_analyst is not None:
            filtered_booked: dict[tuple[date, str], list[dict[str, str | int | bool | None]]] = {}
            for key, entries in booked.items():
                filtered_entries: list[dict[str, str | int | bool | None]] = []
                for entry in entries:
                    user = str(entry.get("user") or "")
                    if self._normalize_person_name(user) == selected_analyst:
                        filtered_entries.append(entry)
                if filtered_entries:
                    filtered_booked[key] = filtered_entries
            booked = filtered_booked
        week_days = [week_start + timedelta(days=offset) for offset in range(7)]
        self._planned_table.setRowCount(len(week_days))
        self._booked_table.setRowCount(len(week_days))

        for row_idx, day in enumerate(week_days):
            day_text = day.strftime("%d.%m.%Y")
            self._planned_table.setItem(row_idx, 0, QTableWidgetItem(day_text))
            self._booked_table.setItem(row_idx, 0, QTableWidgetItem(day_text))

            for col_offset, slot in enumerate(SHIFT_ORDER, start=1):
                key = (day, slot)
                planned_names = planned.get(key, Counter())
                booked_entries = booked.get(key, [])
                booked_names = self._build_booked_counter(booked_entries)
                display_planned_names = planned_names
                if slot == "T" and day.weekday() < 5:
                    display_planned_names = Counter()

                planned_item = QTableWidgetItem(
                    self._format_counter_names(display_planned_names, p_empty="")
                )
                booked_item = QTableWidgetItem(
                    self._format_counter_names(booked_names, p_empty="")
                )

                mismatch_reasons = self._mismatch_reasons(
                    p_planned_names=planned_names,
                    p_booked_names=booked_names,
                    p_bookings=booked_entries,
                    p_day=day,
                    p_slot=slot,
                )
                planned_names_compare = self._normalized_counter(planned_names)
                booked_names_compare = self._normalized_counter(booked_names)

                if planned_names_compare == booked_names_compare and planned_names and not mismatch_reasons:
                    booked_item.setBackground(MATCH_BG)
                    booked_item.setIcon(self._ok_icon)
                    booked_item.setToolTip("Korrekt gebucht")
                elif mismatch_reasons:
                    booked_item.setBackground(MISMATCH_BG)
                    booked_item.setIcon(self._mismatch_icon)
                    booked_item.setToolTip("; ".join(mismatch_reasons))

                self._planned_table.setItem(row_idx, col_offset, planned_item)
                self._booked_table.setItem(row_idx, col_offset, booked_item)

        self._planned_table.resizeColumnsToContents()
        self._booked_table.resizeColumnsToContents()
