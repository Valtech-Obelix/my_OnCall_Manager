from collections import defaultdict
from datetime import date, datetime, timedelta

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from src.infrastructure.timezone_utils import BERLIN, parse_utc_timestamp


APP_TITLE = "Schichtplan anzeigen"
SHIFT_BOUNDARY_HOUR = 1
EARLY_SHIFT_LABEL = "Frühschicht"
DAY_SHIFT_LABEL = "Tagschicht"
LATE_SHIFT_LABEL = "Spätschicht"
EARLY_SHIFT_RANGE = "01:00-09:00"
DAY_SHIFT_RANGE = "09:00-17:00"
LATE_SHIFT_RANGE = "17:00-01:00"


class ShiftPlanViewDialog(QDialog):

    def __init__(self, p_application, p_parent=None):
        super().__init__(p_parent)
        self._application = p_application
        self._entries: list[dict[str, str | int | None]] = []
        self._suspend_parameter_tracking = False
        self._has_rendered_once = False
        self._setup_ui()
        self._load_schedule_references()

    def _setup_ui(self):
        self.setWindowTitle(APP_TITLE)
        self.resize(1050, 620)

        layout = QVBoxLayout()

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)

        self._schedule_combo = QComboBox()
        self._schedule_combo.currentIndexChanged.connect(self._on_schedule_changed)
        form.addRow("Schichtplan:", self._schedule_combo)

        self._view_mode_combo = QComboBox()
        self._view_mode_combo.addItems(["Schichtbezogen", "Tagesbezogen"])
        # Ref: CR-010 – Tagesbezogene Ansicht als Default
        self._view_mode_combo.setCurrentText("Tagesbezogen")
        self._view_mode_combo.currentIndexChanged.connect(self._on_parameter_changed)
        form.addRow("Ansicht:", self._view_mode_combo)

        self._full_range_checkbox = QCheckBox("Gesamten verfügbaren Zeitraum anzeigen")
        # Ref: CR-011 – Default-Zeitraum ist nicht mehr Vollbereich.
        self._full_range_checkbox.setChecked(False)
        self._full_range_checkbox.toggled.connect(self._on_full_range_toggled)
        self._from_date = QDateEdit()
        self._from_date.setCalendarPopup(True)
        self._from_date.setEnabled(True)
        self._from_date.dateChanged.connect(self._on_parameter_changed)

        self._to_date = QDateEdit()
        self._to_date.setCalendarPopup(True)
        self._to_date.setEnabled(True)
        self._to_date.dateChanged.connect(self._on_parameter_changed)

        # Ref: CR-012 – Bis-Datum neben Von-Datum; Checkbox dahinter.
        date_row = QHBoxLayout()
        date_row.addWidget(QLabel("Von:"))
        date_row.addWidget(self._from_date)
        date_row.addWidget(QLabel("Bis:"))
        date_row.addWidget(self._to_date)
        date_row.addWidget(self._full_range_checkbox)
        date_row.addStretch()
        form.addRow("Zeitraum:", date_row)

        layout.addLayout(form)

        button_row = QHBoxLayout()
        # Ref: CR-013 – Buttontext + Aktivierung nur bei geänderten Parametern.
        self._load_button = QPushButton("Anzeige aktualisieren")
        self._load_button.setEnabled(False)
        self._load_button.clicked.connect(self._on_refresh_clicked)
        button_row.addWidget(self._load_button)
        button_row.addStretch()
        layout.addLayout(button_row)

        self._table = QTableWidget()
        self._table.setAlternatingRowColors(True)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self._table)

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
            QMessageBox.information(
                self,
                APP_TITLE,
                "Keine Schichtplan-Referenzen vorhanden."
            )
            return

        self._schedule_combo.setCurrentIndex(0)

    def _on_full_range_toggled(self, p_checked: bool):
        self._from_date.setEnabled(not p_checked)
        self._to_date.setEnabled(not p_checked)
        self._on_parameter_changed()

    def _on_schedule_changed(self, p_index: int):
        if p_index < 0:
            return

        ref = self._schedule_combo.itemData(p_index)
        if not ref:
            return

        self._suspend_parameter_tracking = True
        schedule_id = ref.get("schedule_id", "")
        self._entries = self._application.get_schedule_entries(schedule_id)
        self._set_date_defaults()
        self._suspend_parameter_tracking = False

        if not self._has_rendered_once:
            self._render_table()
            self._has_rendered_once = True
            self._set_refresh_pending(False)
            return
        self._set_refresh_pending(True)

    def _set_date_defaults(self):
        # Ref: CR-011 – Default: laufende 2-Wochen-Montagsblöcke bis Vortag.
        today_local = datetime.now(BERLIN).date()
        default_start = today_local - timedelta(days=today_local.weekday() + 14)
        default_end = today_local - timedelta(days=1)
        self._from_date.setDate(QDate(default_start.year, default_start.month, default_start.day))
        self._to_date.setDate(QDate(default_end.year, default_end.month, default_end.day))

    def _entry_local_date(self, p_entry: dict[str, str | int | None]) -> date:
        return self._display_day(p_entry)

    def _local_start_end(self, p_entry: dict[str, str | int | None]):
        start_local = parse_utc_timestamp(str(p_entry["start_time"])).astimezone(BERLIN)
        end_local = parse_utc_timestamp(str(p_entry["end_time"])).astimezone(BERLIN)
        return start_local, end_local

    def _display_day(self, p_entry: dict[str, str | int | None]) -> date:
        start_local, _ = self._local_start_end(p_entry)
        # 00:00-00:59 gehören noch zur Spätschicht des Vortags.
        if start_local.hour < SHIFT_BOUNDARY_HOUR:
            return start_local.date() - timedelta(days=1)
        return start_local.date()

    def _shift_slot_index(self, p_entry: dict[str, str | int | None]) -> int:
        start_local, _ = self._local_start_end(p_entry)
        shifted_hour = (start_local.hour - SHIFT_BOUNDARY_HOUR) % 24
        if shifted_hour < 8:
            return 0
        if shifted_hour < 16:
            return 1
        return 2

    def _filtered_entries(self) -> list[dict[str, str | int | None]]:
        if self._full_range_checkbox.isChecked():
            return list(self._entries)

        start = self._from_date.date()
        end = self._to_date.date()
        start_date = date(start.year(), start.month(), start.day())
        end_date = date(end.year(), end.month(), end.day())

        filtered = []
        for entry in self._entries:
            entry_date = self._entry_local_date(entry)
            if start_date <= entry_date <= end_date:
                filtered.append(entry)
        return filtered

    def _render_table(self):
        entries = self._sorted_entries_for_display(self._filtered_entries())
        if self._view_mode_combo.currentText() == "Schichtbezogen":
            self._render_shift_rows(entries)
        else:
            self._render_day_rows(entries)

    def _on_parameter_changed(self, *args):
        if self._suspend_parameter_tracking:
            return
        self._set_refresh_pending(True)

    def _on_refresh_clicked(self):
        self._render_table()
        self._set_refresh_pending(False)

    def _set_refresh_pending(self, p_pending: bool):
        self._load_button.setEnabled(p_pending)

    def _sorted_entries_for_display(
        self,
        p_entries: list[dict[str, str | int | None]]
    ) -> list[dict[str, str | int | None]]:
        return sorted(
            p_entries,
            key=lambda e: (
                self._display_day(e),
                self._shift_slot_index(e),
                self._local_start_end(e)[0]
            )
        )

    def _render_shift_rows(self, p_entries: list[dict[str, str | int | None]]):
        self._table.clear()
        headers = ["Datum", "Start", "Ende", "Buchungsname"]
        self._table.setColumnCount(len(headers))
        self._table.setHorizontalHeaderLabels(headers)
        self._table.setRowCount(len(p_entries))

        for row, entry in enumerate(p_entries):
            start_local, end_local = self._local_start_end(entry)

            values = [
                self._display_day(entry).strftime("%d.%m.%Y"),
                start_local.strftime("%H:%M"),
                end_local.strftime("%H:%M"),
                entry.get("buchungsname") or "-",
            ]
            for col, value in enumerate(values):
                self._table.setItem(row, col, QTableWidgetItem(str(value)))

        self._table.resizeColumnsToContents()

    def _render_day_rows(self, p_entries: list[dict[str, str | int | None]]):
        self._table.clear()
        headers = [
            "Datum",
            f"{EARLY_SHIFT_LABEL} ({EARLY_SHIFT_RANGE})",
            f"{DAY_SHIFT_LABEL} ({DAY_SHIFT_RANGE})",
            f"{LATE_SHIFT_LABEL} ({LATE_SHIFT_RANGE})",
        ]
        self._table.setColumnCount(len(headers))
        self._table.setHorizontalHeaderLabels(headers)

        grouped: dict[date, dict[int, list[str]]] = defaultdict(
            lambda: defaultdict(list)
        )
        for entry in p_entries:
            slot = self._shift_slot_index(entry)
            display_day = self._display_day(entry)
            label = str(entry.get("buchungsname") or "-")
            grouped[display_day][slot].append(label)

        days = sorted(grouped.keys())
        self._table.setRowCount(len(days))
        for row, day in enumerate(days):
            self._table.setItem(row, 0, QTableWidgetItem(day.strftime("%d.%m.%Y")))
            for col in range(3):
                names = grouped[day].get(col, [])
                if not names:
                    value = "-"
                elif len(names) == 1:
                    value = names[0]
                else:
                    value = ", ".join(names)
                self._table.setItem(row, col + 1, QTableWidgetItem(value))

        self._table.resizeColumnsToContents()
