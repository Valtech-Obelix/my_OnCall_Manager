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
        form.addRow("Monat:", self._month_combo)
        layout.addLayout(form)

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
        layout.addWidget(self._table)
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

    def _refresh_table(self):
        year = int(self._year_input.value())
        month = int(self._month_combo.currentData())
        rows = self._application.get_monthly_compensation_summary(year, month)

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
                self._table.setItem(row_index, col_index, QTableWidgetItem(value))

        self._table.resizeColumnsToContents()
        self._total_label.setText(f"Gesamtsumme: {total} EUR")
