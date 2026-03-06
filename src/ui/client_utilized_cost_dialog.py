from    datetime                                           import  datetime
from    decimal                                            import  Decimal, InvalidOperation

from    PySide6.QtCore                                     import  Qt
from    PySide6.QtWidgets                                  import  (
                                                                 QComboBox,
                                                                 QDialog,
                                                                 QDialogButtonBox,
                                                                 QFormLayout,
                                                                 QLabel,
                                                                 QTableWidget,
                                                                 QTableWidgetItem,
                                                                 QVBoxLayout,
                                                             )


APP_TITLE = "Testdialog – Client Utilized Kosten"


class ClientUtilizedCostDialog(QDialog):
    def __init__(self, p_application, p_parent=None):
        super().__init__(p_parent)
        self._application = p_application
        self._ui_ready = False
        self._current_year = 0
        self._current_month = 0
        self._current_location_filter = "GER"
        self._setup_ui()
        self._ui_ready = True
        self._set_default_month()
        self._refresh_table()

    def _setup_ui(self):
        self.setWindowTitle(APP_TITLE)
        self.resize(980, 560)

        layout = QVBoxLayout()

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)

        self._year_input = QComboBox()
        current_year = datetime.now().year
        for year in range(current_year - 2, current_year + 2):
            self._year_input.addItem(str(year), year)
        self._year_input.currentIndexChanged.connect(self._refresh_table)
        self._year_input.setEditable(True)

        self._month_combo = QComboBox()
        for month in range(1, 13):
            self._month_combo.addItem(f"{month:02d}", month)
        self._month_combo.currentIndexChanged.connect(self._refresh_table)

        self._location_combo = QComboBox()
        self._location_combo.currentIndexChanged.connect(self._refresh_table)
        self._load_locations()

        form.addRow("Jahr:", self._year_input)
        form.addRow("Monat:", self._month_combo)
        form.addRow("Standort:", self._location_combo)
        layout.addLayout(form)

        self._table = QTableWidget()
        self._table.setAlternatingRowColors(True)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setSelectionMode(QTableWidget.SingleSelection)
        self._table.setColumnCount(8)
        self._table.setHorizontalHeaderLabels(
            [
                "Buchungsdatum",
                "Buchungsname",
                "Task",
                "Stunden",
                "Stundensatz (EUR)",
                "Kosten (EUR)",
                "Gehaltsgruppe",
                "Status",
            ]
        )
        layout.addWidget(self._table)

        self._total_label = QLabel("Gesamt (berechnet): 0 EUR")
        layout.addWidget(self._total_label)

        button_row = QVBoxLayout()
        close_button = QDialogButtonBox.StandardButton.Close
        buttons = QDialogButtonBox(close_button)
        buttons.rejected.connect(self.close)
        button_row.addWidget(buttons)
        layout.addLayout(button_row)

        self.setLayout(layout)

    def _set_default_month(self):
        now = datetime.now()
        default_year = now.year
        default_month = now.month - 1
        if default_month == 0:
            default_month = 12
            default_year -= 1

        for index in range(self._year_input.count()):
            if int(self._year_input.itemData(index)) == default_year:
                self._year_input.setCurrentIndex(index)
                break

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
        if not self._ui_ready:
            return

        year_data = self._year_input.currentData()
        month_data = self._month_combo.currentData()
        if year_data is None or month_data is None:
            return

        location_filter = str(self._location_combo.currentData() or "GER")
        self._current_year = int(year_data)
        self._current_month = int(month_data)
        self._current_location_filter = location_filter

        rows = self._application.get_client_utilized_costs_for_month(
            p_year=self._current_year,
            p_month=self._current_month,
            p_location_filter=self._current_location_filter,
        )

        self._table.setRowCount(len(rows))
        total_cost = Decimal("0")
        for row_index, row_data in enumerate(rows):
            values = [
                str(row_data.get("booking_date", "")),
                str(row_data.get("buchungsname", "")),
                str(row_data.get("task_name", "")),
                str(row_data.get("hours", "")),
                str(row_data.get("rate_eur", "")),
                str(row_data.get("cost_eur", "")),
                str(row_data.get("gehaltsgruppe", "")),
                str(row_data.get("status", "")),
            ]
            for col_index, value in enumerate(values):
                self._table.setItem(row_index, col_index, QTableWidgetItem(value))

            try:
                total_cost += Decimal(str(row_data.get("cost_eur", "0")).replace(",", "."))
            except InvalidOperation:
                pass

        self._table.resizeColumnsToContents()
        self._total_label.setText(f"Gesamt (berechnet): {self._format_currency(total_cost)} EUR")

    def _format_currency(self, p_value: Decimal) -> str:
        value = p_value.normalize()
        text = format(value, "f")
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        return text or "0"
