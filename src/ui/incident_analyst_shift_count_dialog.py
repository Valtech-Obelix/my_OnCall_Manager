from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
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


APP_TITLE = "Aktive IA nach Schichtanzahl"


class IncidentAnalystShiftCountDialog(QDialog):
    def __init__(self, p_application, p_parent=None):
        super().__init__(p_parent)
        self._application = p_application
        self._setup_ui()
        self._load_initial()

    def _setup_ui(self):
        self.setWindowTitle(APP_TITLE)
        self.resize(760, 540)

        layout = QVBoxLayout()

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)

        self._weeks_input = QSpinBox()
        self._weeks_input.setMinimum(1)
        self._weeks_input.setMaximum(260)
        form.addRow("Letzte n Wochen:", self._weeks_input)

        layout.addLayout(form)

        button_row = QHBoxLayout()
        self._refresh_button = QPushButton("Anzeigen")
        self._refresh_button.clicked.connect(self._refresh_table)
        button_row.addWidget(self._refresh_button)
        button_row.addStretch()
        layout.addLayout(button_row)

        self._table = QTableWidget()
        self._table.setAlternatingRowColors(True)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setColumnCount(2)
        self._table.setHorizontalHeaderLabels(["Buchungsname", "Schichtanzahl"])
        layout.addWidget(self._table)

        self.setLayout(layout)

    def _load_initial(self):
        weeks = self._application.get_last_shift_count_weeks()
        self._weeks_input.setValue(weeks)
        self._refresh_table()

    def _refresh_table(self):
        weeks = int(self._weeks_input.value())
        self._application.set_last_shift_count_weeks(weeks)
        rows = self._application.get_active_analyst_shift_counts_last_weeks(weeks)

        self._table.setRowCount(len(rows))
        for row_index, row_data in enumerate(rows):
            self._table.setItem(
                row_index,
                0,
                QTableWidgetItem(str(row_data.get("buchungsname", "")))
            )
            self._table.setItem(
                row_index,
                1,
                QTableWidgetItem(str(row_data.get("shift_count", 0)))
            )

        self._table.resizeColumnsToContents()
