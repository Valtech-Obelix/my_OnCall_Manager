from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from src.infrastructure.timezone_utils import BERLIN


APP_TITLE = "Monatsabrechnung IA-Auszahlung"


class MonthlyCompensationDialog(QDialog):
    def __init__(self, p_application, p_parent=None):
        super().__init__(p_parent)
        self._application = p_application
        self._total_label = QLabel("Gesamtsumme: 0 EUR")
        self._current_year = 0
        self._current_month = 0
        self._current_location_filter = "GER"
        self._setup_ui()
        self._set_default_month()
        self._refresh_table()

    def _setup_ui(self):
        self.setWindowTitle(APP_TITLE)
        self.resize(980, 620)

        layout = QVBoxLayout()

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)

        self._year_input = QSpinBox()
        self._year_input.setRange(2020, 2100)
        self._year_input.valueChanged.connect(self._refresh_table)
        form.addRow("Jahr:", self._year_input)

        self._month_combo = QComboBox()
        for month in range(1, 13):
            self._month_combo.addItem(f"{month:02d}", month)
        self._month_combo.currentIndexChanged.connect(self._refresh_table)

        self._location_combo = QComboBox()
        self._location_combo.currentIndexChanged.connect(self._refresh_table)
        self._load_locations()

        month_location_row = QHBoxLayout()
        month_location_row.addWidget(self._month_combo)
        month_location_row.addWidget(QLabel("Standort:"))
        month_location_row.addWidget(self._location_combo)
        month_location_row.addStretch()
        form.addRow("Monat:", month_location_row)
        layout.addLayout(form)

        tables_row = QHBoxLayout()

        self._table = QTableWidget()
        self._table.setAlternatingRowColors(True)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setColumnCount(6)
        self._table.setHorizontalHeaderLabels(
            [
                "Buchungsname",
                "Standort",
                "Früh",
                "Tag",
                "Spät",
                "Auszahlung (EUR)",
            ]
        )
        self._table.itemSelectionChanged.connect(self._on_summary_selection_changed)
        tables_row.addWidget(self._table, stretch=3)

        self._detail_table = QTableWidget()
        self._detail_table.setAlternatingRowColors(True)
        self._detail_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._detail_table.setColumnCount(7)
        self._detail_table.setHorizontalHeaderLabels(
            [
                "Buchungsdatum",
                "User",
                "Schicht",
                "Tagtyp",
                "Betrag (EUR)",
                "Notiz",
                "Quelle",
            ]
        )
        tables_row.addWidget(self._detail_table, stretch=4)

        layout.addLayout(tables_row)
        layout.addWidget(self._total_label)

        button_row = QHBoxLayout()
        button_row.addStretch()
        close_button = QPushButton("Schließen")
        close_button.clicked.connect(self.close)
        button_row.addWidget(close_button)
        layout.addLayout(button_row)

        self.setLayout(layout)

    def _set_default_month(self):
        now = datetime.now(BERLIN)
        default_year = now.year
        default_month = now.month - 1
        if default_month == 0:
            default_month = 12
            default_year -= 1

        self._year_input.setValue(default_year)
        month_index = self._month_combo.findData(default_month)
        if month_index >= 0:
            self._month_combo.setCurrentIndex(month_index)

        ger_index = self._location_combo.findData("GER")
        if ger_index >= 0:
            self._location_combo.setCurrentIndex(ger_index)

    def _load_locations(self):
        self._location_combo.clear()
        locations = self._application.get_oncall_locations()
        for location in locations:
            location_id = str(location.get("id", "")).strip().upper()
            location_name = str(location.get("name", "")).strip()
            label = f"{location_name} ({location_id})" if location_name else location_id
            self._location_combo.addItem(label, location_id)

        if self._location_combo.count() == 0:
            self._location_combo.addItem("Deutschland (GER)", "GER")
            self._location_combo.addItem("Indien (IND)", "IND")

    def _refresh_table(self):
        year = int(self._year_input.value())
        month = int(self._month_combo.currentData())
        location_filter = str(self._location_combo.currentData() or "GER")
        self._current_year = year
        self._current_month = month
        self._current_location_filter = location_filter
        rows = self._application.get_monthly_compensation_summary(
            year,
            month,
            location_filter,
        )

        self._table.setRowCount(len(rows))
        total = 0
        for row_index, row_data in enumerate(rows):
            amount = int(row_data.get("total_amount_eur", 0))
            total += amount
            values = [
                str(row_data.get("buchungsname", "")),
                str(row_data.get("oncall_location_id", "")),
                str(row_data.get("shift_count_f", 0)),
                str(row_data.get("shift_count_t", 0)),
                str(row_data.get("shift_count_s", 0)),
                str(amount),
            ]
            for col_index, value in enumerate(values):
                item = QTableWidgetItem(value)
                if col_index == 0:
                    item.setData(Qt.UserRole, int(row_data.get("analyst_id", 0)))
                self._table.setItem(row_index, col_index, item)

        self._table.resizeColumnsToContents()
        self._total_label.setText(f"Gesamtsumme: {total} EUR")
        if len(rows) > 0:
            self._table.selectRow(0)
        else:
            self._detail_table.setRowCount(0)

    def _on_summary_selection_changed(self):
        selected_items = self._table.selectedItems()
        if not selected_items:
            self._detail_table.setRowCount(0)
            return
        analyst_id = selected_items[0].data(Qt.UserRole)
        if not analyst_id:
            self._detail_table.setRowCount(0)
            return

        rows = self._application.get_monthly_compensation_details(
            p_year=self._current_year,
            p_month=self._current_month,
            p_analyst_id=int(analyst_id),
            p_location_filter=self._current_location_filter,
        )
        self._detail_table.setRowCount(len(rows))
        for row_index, row_data in enumerate(rows):
            values = [
                str(row_data.get("booking_date", "")),
                str(row_data.get("user", "")),
                str(row_data.get("slot", "")),
                str(row_data.get("day_type", "")),
                str(row_data.get("amount_eur", 0)),
                str(row_data.get("notes", "")),
                str(row_data.get("source_file", "")),
            ]
            for col_index, value in enumerate(values):
                self._detail_table.setItem(row_index, col_index, QTableWidgetItem(value))
        self._detail_table.resizeColumnsToContents()
