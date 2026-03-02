import csv
import re
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QStyle,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from src.infrastructure.timezone_utils import BERLIN, parse_utc_timestamp


APP_TITLE = "OpsGenie vs. Buchungen vergleichen"
SHIFT_BOUNDARY_HOUR = 1
SHIFT_ORDER = ["F", "T", "S"]
MATCH_BG = QColor("#dbeafe")
MISMATCH_BG = QColor("#ffedd5")


class ShiftBookingCompareDialog(QDialog):
    def __init__(self, p_application, p_parent=None):
        super().__init__(p_parent)
        self._application = p_application
        self._entries: list[dict[str, str | int | None]] = []
        self._ok_icon = self.style().standardIcon(QStyle.SP_DialogApplyButton)
        self._mismatch_icon = self.style().standardIcon(QStyle.SP_MessageBoxWarning)
        self._setup_ui()
        self._load_analyst_filter()
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

        self._week_start = QDateEdit()
        self._week_start.setCalendarPopup(True)
        today = datetime.now(BERLIN).date()
        monday = today - timedelta(days=today.weekday() + 7)
        self._week_start.setDate(QDate(monday.year, monday.month, monday.day))
        form.addRow("Wochenstart:", self._week_start)

        self._analyst_combo = QComboBox()
        self._analyst_combo.currentIndexChanged.connect(self._render_comparison)
        form.addRow("Incident Analyst:", self._analyst_combo)

        row = QHBoxLayout()
        self._refresh_button = QPushButton("Vergleich anzeigen")
        self._refresh_button.clicked.connect(self._render_comparison)
        row.addWidget(self._refresh_button)
        row.addStretch()
        form.addRow("", row)

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

    def _on_schedule_changed(self, p_index: int):
        if p_index < 0:
            return
        ref = self._schedule_combo.itemData(p_index)
        if not ref:
            return
        schedule_id = ref.get("schedule_id", "")
        self._entries = self._application.get_schedule_entries(schedule_id)
        self._render_comparison()

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
    ) -> dict[tuple[date, str], Counter[str]]:
        result: dict[tuple[date, str], Counter[str]] = {}
        data_path = Path(__file__).resolve().parents[2] / "data"
        for file_path in sorted(data_path.glob("*.csv")):
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
                required = ["Date", "User", "Task - Task type", "Notes"]
                if any(key not in index_map for key in required):
                    continue

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

                    user = row[index_map["User"]].strip()
                    key = (booking_date, slot)
                    result.setdefault(key, Counter())[user] += 1
        return result

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
        start = self._week_start.date()
        week_start = date(start.year(), start.month(), start.day())
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
            filtered_booked: dict[tuple[date, str], Counter[str]] = {}
            for key, names in booked.items():
                local_counter: Counter[str] = Counter()
                for name, count in names.items():
                    if self._normalize_person_name(name) == selected_analyst:
                        local_counter[name] += count
                if local_counter:
                    filtered_booked[key] = local_counter
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
                booked_names = booked.get(key, Counter())
                display_planned_names = planned_names
                if slot == "T" and day.weekday() < 5:
                    display_planned_names = Counter()

                planned_item = QTableWidgetItem(
                    self._format_counter_names(display_planned_names, p_empty="")
                )
                booked_item = QTableWidgetItem(
                    self._format_counter_names(booked_names, p_empty="")
                )

                planned_names_compare = self._normalized_counter(planned_names)
                booked_names_compare = self._normalized_counter(booked_names)
                is_weekday_day_shift_without_booking = (
                    slot == "T"
                    and day.weekday() < 5
                    and not booked_names
                )

                if planned_names_compare == booked_names_compare and planned_names:
                    booked_item.setBackground(MATCH_BG)
                    booked_item.setIcon(self._ok_icon)
                    booked_item.setToolTip("Korrekt gebucht")
                elif planned_names_compare != booked_names_compare and not is_weekday_day_shift_without_booking:
                    booked_item.setBackground(MISMATCH_BG)
                    booked_item.setIcon(self._mismatch_icon)
                    booked_item.setToolTip("Abweichung zwischen Plan und Buchung")

                self._planned_table.setItem(row_idx, col_offset, planned_item)
                self._booked_table.setItem(row_idx, col_offset, booked_item)

        self._planned_table.resizeColumnsToContents()
        self._booked_table.resizeColumnsToContents()
