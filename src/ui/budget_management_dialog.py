from datetime import date

from PySide6.QtCharts import (
    QBarCategoryAxis,
    QBarSeries,
    QBarSet,
    QChart,
    QChartView,
    QValueAxis,
)
from PySide6.QtGui import QPainter
from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QDateEdit,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.domain.exceptions import DomainException


APP_TITLE = "Budgetverwaltung"


class BudgetManagementDialog(QDialog):
    def __init__(self, p_application, p_parent=None):
        super().__init__(p_parent)
        self._application = p_application
        self._selected_source_id: int | None = None
        self._selected_period_id: int | None = None
        self._is_source_edit_mode = False
        self._is_period_edit_mode = False
        self._timeline_chart = QChart()
        self._timeline_chart_view = QChartView(self._timeline_chart)

        self._setup_ui()
        self._refresh_sources()
        self._refresh_timeline()
        self._set_source_fields_enabled(False)
        self._set_period_fields_enabled(False)

    def _setup_ui(self) -> None:
        self.setWindowTitle(APP_TITLE)
        self.resize(1180, 740)

        layout = QVBoxLayout()
        tab_widget = QTabWidget()

        manage_tab = QWidget()
        manage_tab_layout = QVBoxLayout()
        manage_tab_layout.addWidget(self._build_source_section())
        manage_tab_layout.addWidget(self._build_period_section())
        manage_tab.setLayout(manage_tab_layout)
        tab_widget.addTab(manage_tab, "Budgetdaten")

        timeline_tab = QWidget()
        timeline_tab.setLayout(self._build_timeline_section())
        tab_widget.addTab(timeline_tab, "Monatsverlauf")

        layout.addWidget(tab_widget)

        button_row = QHBoxLayout()
        button_row.addStretch()
        close_button = QPushButton("Dialog schließen")
        close_button.clicked.connect(self.close)
        button_row.addWidget(close_button)
        layout.addLayout(button_row)

        self.setLayout(layout)

    def _build_source_section(self) -> QWidget:
        section = QGroupBox("Kunden")
        layout = QVBoxLayout()

        self._source_table = QTableWidget()
        self._source_table.setColumnCount(3)
        self._source_table.setHorizontalHeaderLabels(["ID", "Name", "Aktiv"])
        self._source_table.setSelectionBehavior(self._source_table.SelectionBehavior.SelectRows)
        self._source_table.setSelectionMode(self._source_table.SelectionMode.SingleSelection)
        self._source_table.setEditTriggers(self._source_table.EditTrigger.NoEditTriggers)
        self._source_table.itemSelectionChanged.connect(self._on_source_selected)
        layout.addWidget(self._source_table)

        filter_layout = QHBoxLayout()
        self._show_inactive_checkbox = QCheckBox("Inaktive mit anzeigen")
        self._show_inactive_checkbox.stateChanged.connect(self._on_show_inactive_changed)
        filter_layout.addWidget(self._show_inactive_checkbox)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        form = QFormLayout()
        self._source_name_input = QLineEdit()
        self._source_name_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._source_active_input = QCheckBox("Aktiv")
        self._source_active_input.setChecked(True)
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignLeft)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        form.addRow("Kunde:", self._source_name_input)
        form.addRow("Status:", self._source_active_input)
        layout.addLayout(form)

        button_row = QHBoxLayout()
        self._source_new_button = QPushButton("Neu")
        self._source_new_button.clicked.connect(self._on_source_new_clicked)
        self._source_edit_button = QPushButton("Bearbeiten")
        self._source_edit_button.clicked.connect(self._on_source_edit_clicked)
        self._source_save_button = QPushButton("Speichern")
        self._source_save_button.clicked.connect(self._on_source_save_clicked)
        self._source_delete_button = QPushButton("Löschen")
        self._source_delete_button.clicked.connect(self._on_source_delete_clicked)
        button_row.addWidget(self._source_new_button)
        button_row.addWidget(self._source_edit_button)
        button_row.addWidget(self._source_save_button)
        button_row.addWidget(self._source_delete_button)
        button_row.addStretch()
        layout.addLayout(button_row)

        section.setLayout(layout)
        return section

    def _build_period_section(self) -> QWidget:
        section = QGroupBox("Verträge")
        layout = QVBoxLayout()

        self._period_table = QTableWidget()
        self._period_table.setColumnCount(5)
        self._period_table.setHorizontalHeaderLabels([
            "ID",
            "Vertragstitel",
            "Gueltig ab",
            "Gueltig bis",
            "Betrag EUR",
        ])
        self._period_table.setSelectionBehavior(self._period_table.SelectionBehavior.SelectRows)
        self._period_table.setSelectionMode(self._period_table.SelectionMode.SingleSelection)
        self._period_table.setEditTriggers(self._period_table.EditTrigger.NoEditTriggers)
        self._period_table.itemSelectionChanged.connect(self._on_period_selected)
        layout.addWidget(self._period_table)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignLeft)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

        self._period_note_input = QLineEdit()
        self._period_note_input.setPlaceholderText("Vertragstitel")
        self._period_note_input.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self._period_from_input = QDateEdit()
        self._period_from_input.setCalendarPopup(True)
        self._period_from_input.setDisplayFormat("dd.MM.yyyy")
        self._period_from_input.setDate(QDate.currentDate())
        self._period_to_input = QDateEdit()
        self._period_to_input.setCalendarPopup(True)
        self._period_to_input.setDisplayFormat("dd.MM.yyyy")
        self._period_to_input.setDate(QDate.currentDate())
        self._period_amount_input = QLineEdit()
        self._period_amount_input.setPlaceholderText("z.B. 1200.00")
        self._period_amount_input.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        date_range_layout = QHBoxLayout()
        date_range_layout.addWidget(QLabel("Beginn:"))
        date_range_layout.addWidget(self._period_from_input)
        date_range_layout.addWidget(QLabel("Ende:"))
        date_range_layout.addWidget(self._period_to_input)
        date_range_layout.addStretch()

        form.addRow("Vertragstitel:", self._period_note_input)
        form.addRow("", date_range_layout)
        form.addRow("Betrag:", self._period_amount_input)
        layout.addLayout(form)

        button_row = QHBoxLayout()
        self._period_new_button = QPushButton("Neu")
        self._period_new_button.clicked.connect(self._on_period_new_clicked)
        self._period_edit_button = QPushButton("Bearbeiten")
        self._period_edit_button.clicked.connect(self._on_period_edit_clicked)
        self._period_save_button = QPushButton("Speichern")
        self._period_save_button.clicked.connect(self._on_period_save_clicked)
        self._period_delete_button = QPushButton("Löschen")
        self._period_delete_button.clicked.connect(self._on_period_delete_clicked)
        button_row.addWidget(self._period_new_button)
        button_row.addWidget(self._period_edit_button)
        button_row.addWidget(self._period_save_button)
        button_row.addWidget(self._period_delete_button)
        button_row.addStretch()
        layout.addLayout(button_row)

        section.setLayout(layout)
        return section

    def _build_timeline_section(self) -> QVBoxLayout:
        layout = QVBoxLayout()

        form = QHBoxLayout()
        self._timeline_from_year = QSpinBox()
        self._timeline_from_year.setRange(2020, 2100)
        self._timeline_from_year.setValue(date.today().year)
        self._timeline_to_year = QSpinBox()
        self._timeline_to_year.setRange(2020, 2100)
        self._timeline_to_year.setValue(date.today().year)
        refresh_button = QPushButton("Ansicht aktualisieren")
        refresh_button.clicked.connect(self._refresh_timeline)

        form.addWidget(QLabel("Von Jahr:"))
        form.addWidget(self._timeline_from_year)
        form.addWidget(QLabel("Bis Jahr:"))
        form.addWidget(self._timeline_to_year)
        form.addWidget(refresh_button)
        form.addStretch()
        layout.addLayout(form)

        self._timeline_chart_view.setRenderHint(QPainter.Antialiasing, True)
        self._timeline_chart_view.setMinimumHeight(430)
        layout.addWidget(self._timeline_chart_view)
        return layout

    # ------------------------------------------------------------------
    # Quellen
    # ------------------------------------------------------------------
    def _on_show_inactive_changed(self):
        self._refresh_sources()
        self._clear_source_form()

    def _refresh_sources(self) -> None:
        include_inactive = bool(self._show_inactive_checkbox.isChecked())
        sources = self._application.get_budget_sources(p_include_inactive=include_inactive)
        self._source_table.setRowCount(len(sources))
        for row_index, source in enumerate(sources):
            id_item = QTableWidgetItem(str(source["id"]))
            id_item.setData(Qt.UserRole, int(source["id"]))
            self._source_table.setItem(row_index, 0, id_item)
            self._source_table.setItem(row_index, 1, QTableWidgetItem(str(source.get("name", ""))))
            self._source_table.setItem(row_index, 2, QTableWidgetItem("Ja" if int(source.get("is_active", 1)) else "Nein"))
        self._source_table.resizeColumnsToContents()
        if self._source_table.rowCount() == 0:
            self._source_table.clearContents()

    def _on_source_selected(self) -> None:
        row = self._source_table.currentRow()
        if row < 0:
            return
        source_id_item = self._source_table.item(row, 0)
        if source_id_item is None:
            return
        source_id = int(source_id_item.data(Qt.UserRole))
        try:
            source = self._application.get_budget_source(source_id)
        except DomainException as exc:
            QMessageBox.warning(self, APP_TITLE, str(exc))
            return

        self._selected_source_id = int(source.get("id"))
        self._source_name_input.setText(str(source.get("name", "")))
        self._source_active_input.setChecked(bool(int(source.get("is_active", 1))))
        self._is_source_edit_mode = False
        self._set_source_fields_enabled(False)
        self._set_primary_button(self._source_edit_button)

        self._refresh_periods()

    def _on_source_new_clicked(self) -> None:
        self._selected_source_id = None
        self._is_source_edit_mode = False
        self._source_name_input.clear()
        self._source_active_input.setChecked(True)
        self._set_source_fields_enabled(True)
        self._set_primary_button(self._source_save_button)
        self._source_name_input.setFocus()
        self._clear_period_form()
        self._set_period_fields_enabled(False)
        self._source_name_input.setEnabled(True)
        self._source_active_input.setEnabled(True)

    def _on_source_edit_clicked(self) -> None:
        if self._selected_source_id is None:
            QMessageBox.information(self, APP_TITLE, "Bitte zuerst eine Budgetquelle auswählen.")
            return
        self._is_source_edit_mode = True
        self._set_source_fields_enabled(True)
        self._source_name_input.setEnabled(True)
        self._source_active_input.setEnabled(True)
        self._set_primary_button(self._source_save_button)
        self._source_name_input.setFocus()

    def _on_source_save_clicked(self) -> None:
        source_name = self._source_name_input.text().strip()
        if self._is_source_edit_mode and self._selected_source_id is not None:
            try:
                self._application.rename_budget_source(
                    p_source_id=self._selected_source_id,
                    p_name=source_name,
                )
                self._application.set_budget_source_active(
                    p_source_id=self._selected_source_id,
                    p_is_active=self._source_active_input.isChecked(),
                )
            except DomainException as exc:
                QMessageBox.warning(self, APP_TITLE, str(exc))
                return
        else:
            if not source_name:
                QMessageBox.warning(self, APP_TITLE, "Der Quellenname ist erforderlich.")
                return
            try:
                self._selected_source_id = self._application.create_budget_source(source_name)
            except DomainException as exc:
                QMessageBox.warning(self, APP_TITLE, str(exc))
                return
        self._application.set_budget_source_active(
            p_source_id=self._selected_source_id,
            p_is_active=True,
        )

        self._refresh_sources()
        self._refresh_periods()
        self._set_source_fields_enabled(False)
        self._is_source_edit_mode = False
        self._set_primary_button(self._source_edit_button)

    def _on_source_delete_clicked(self) -> None:
        if self._selected_source_id is None:
            QMessageBox.information(self, APP_TITLE, "Bitte zuerst eine Budgetquelle auswählen.")
            return
        reply = QMessageBox.question(
            self,
            APP_TITLE,
            "Ausgewählte Budgetquelle inklusive Zeiträume löschen?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        try:
            self._application.delete_budget_source(self._selected_source_id)
        except DomainException as exc:
            QMessageBox.warning(self, APP_TITLE, str(exc))
            return

        self._clear_source_form()
        self._refresh_sources()
        self._refresh_periods()

    # ------------------------------------------------------------------
    # Zeiträume
    # ------------------------------------------------------------------
    def _refresh_periods(self) -> None:
        self._period_table.setRowCount(0)
        if self._selected_source_id is None:
            return
        periods = self._application.get_budget_periods(p_budget_source_id=self._selected_source_id)
        self._period_table.setRowCount(len(periods))
        for row_index, period in enumerate(periods):
            self._period_table.setItem(row_index, 0, QTableWidgetItem(str(period["id"])))
            self._period_table.setItem(row_index, 1, QTableWidgetItem(str(period["note"])))
            self._period_table.setItem(row_index, 2, QTableWidgetItem(str(period["gueltig_ab"])))
            self._period_table.setItem(row_index, 3, QTableWidgetItem(str(period["gueltig_bis"])))
            self._period_table.setItem(row_index, 4, QTableWidgetItem(str(period["betrag_eur"])))
        self._period_table.resizeColumnsToContents()
        self._period_table.clearSelection()
        self._selected_period_id = None
        self._set_period_fields_enabled(bool(self._selected_source_id))
        self._set_primary_button(self._period_new_button)

    def _on_period_selected(self) -> None:
        row = self._period_table.currentRow()
        if row < 0:
            return
        period_id_item = self._period_table.item(row, 0)
        note_item = self._period_table.item(row, 1)
        from_item = self._period_table.item(row, 2)
        to_item = self._period_table.item(row, 3)
        amount_item = self._period_table.item(row, 4)
        if (
            period_id_item is None
            or from_item is None
            or amount_item is None
            or to_item is None
        ):
            return
        self._selected_period_id = int(period_id_item.text())
        self._period_note_input.setText(str(note_item.text() if note_item is not None else ""))
        self._period_from_input.setDate(QDate.fromString(from_item.text(), "yyyy-MM-dd"))
        self._period_to_input.setDate(QDate.fromString(to_item.text(), "yyyy-MM-dd"))
        self._period_amount_input.setText(str(amount_item.text()))
        self._is_period_edit_mode = False
        self._set_period_fields_enabled(True)
        self._set_primary_button(self._period_edit_button)

    def _on_period_new_clicked(self) -> None:
        if self._selected_source_id is None:
            QMessageBox.information(self, APP_TITLE, "Bitte zuerst eine Budgetquelle auswählen.")
            return
        self._selected_period_id = None
        self._is_period_edit_mode = True
        self._clear_period_form()
        self._set_period_fields_enabled(True)
        self._set_primary_button(self._period_save_button)
        self._period_note_input.setFocus()

    def _on_period_edit_clicked(self) -> None:
        if self._selected_period_id is None:
            QMessageBox.information(self, APP_TITLE, "Bitte zuerst einen Zeitraum auswählen.")
            return
        self._is_period_edit_mode = True
        self._set_period_fields_enabled(True)
        self._set_primary_button(self._period_save_button)
        self._period_note_input.setFocus()

    def _on_period_save_clicked(self) -> None:
        if self._selected_source_id is None:
            QMessageBox.information(self, APP_TITLE, "Bitte zuerst eine Budgetquelle auswählen.")
            return
        try:
            period_from = date(
                self._period_from_input.date().year(),
                self._period_from_input.date().month(),
                self._period_from_input.date().day(),
            )
            period_to = date(
                self._period_to_input.date().year(),
                self._period_to_input.date().month(),
                self._period_to_input.date().day(),
            )
            amount = self._parse_amount(self._period_amount_input.text())
            note = self._period_note_input.text().strip() or None
        except DomainException as exc:
            QMessageBox.warning(self, APP_TITLE, str(exc))
            return

        try:
            if self._is_period_edit_mode and self._selected_period_id is not None:
                self._application.update_budget_period(
                    p_period_id=self._selected_period_id,
                    p_gueltig_ab=period_from,
                    p_betrag_eur=amount,
                    p_gueltig_bis=period_to,
                    p_note=note,
                )
            else:
                self._application.create_budget_period(
                    p_budget_source_id=self._selected_source_id,
                    p_gueltig_ab=period_from,
                    p_gueltig_bis=period_to,
                    p_betrag_eur=amount,
                    p_note=note,
                )
        except DomainException as exc:
            QMessageBox.warning(self, APP_TITLE, str(exc))
            return

        self._is_period_edit_mode = False
        self._clear_period_form()
        self._set_period_fields_enabled(False)
        self._refresh_periods()
        self._refresh_timeline()

    def _on_period_delete_clicked(self) -> None:
        if self._selected_period_id is None:
            QMessageBox.information(self, APP_TITLE, "Bitte zuerst einen Zeitraum auswählen.")
            return
        reply = QMessageBox.question(
            self,
            APP_TITLE,
            "Ausgewählten Zeitraum wirklich löschen?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        try:
            self._application.delete_budget_period(self._selected_period_id)
        except DomainException as exc:
            QMessageBox.warning(self, APP_TITLE, str(exc))
            return
        self._selected_period_id = None
        self._refresh_periods()
        self._refresh_timeline()

    # ------------------------------------------------------------------
    # Verlauf
    # ------------------------------------------------------------------
    def _refresh_timeline(self) -> None:
        year_from = int(self._timeline_from_year.value())
        year_to = int(self._timeline_to_year.value())
        if year_to < year_from:
            QMessageBox.warning(self, APP_TITLE, "Bis Jahr darf nicht kleiner als Von Jahr sein.")
            return

        rows = self._application.get_budget_timeline(
            p_from=date(year_from, 1, 1),
            p_to=date(year_to, 12, 31),
        )
        self._timeline_chart.removeAllSeries()
        axis_x_existing = self._timeline_chart.axisX()
        if axis_x_existing is not None:
            self._timeline_chart.removeAxis(axis_x_existing)
        axis_y_existing = self._timeline_chart.axisY()
        if axis_y_existing is not None:
            self._timeline_chart.removeAxis(axis_y_existing)

        self._timeline_chart.setTitle("Monatsbudgetverlauf")
        self._timeline_chart.legend().setVisible(False)

        categories = [str(row.get("label", "")) for row in rows]
        values = [float(row.get("amount_eur", 0.0)) for row in rows]

        bar_set = QBarSet("Budget")
        for value in values:
            bar_set.append(value)
        series = QBarSeries()
        series.append(bar_set)
        self._timeline_chart.addSeries(series)

        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        self._timeline_chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)

        max_value = max(values) if values else 0.0
        axis_y = QValueAxis()
        axis_y.setLabelFormat("%.2f EUR")
        axis_y.setRange(0.0, max(1.0, max_value))
        axis_y.setMinorTickCount(0)
        self._timeline_chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _clear_source_form(self) -> None:
        self._selected_source_id = None
        self._source_name_input.clear()
        self._source_active_input.setChecked(True)
        self._set_primary_button(self._source_new_button)
        self._source_table.clearSelection()
        self._clear_period_form()
        self._set_period_fields_enabled(False)

    def _clear_period_form(self) -> None:
        self._selected_period_id = None
        self._period_from_input.setDate(QDate.currentDate())
        self._period_to_input.setDate(QDate.currentDate())
        self._period_amount_input.clear()
        self._period_note_input.clear()
        self._period_table.clearSelection()

    def _set_source_fields_enabled(self, p_enabled: bool) -> None:
        self._source_name_input.setEnabled(p_enabled)
        self._source_active_input.setEnabled(p_enabled)

    def _set_period_fields_enabled(self, p_enabled: bool) -> None:
        fields_enabled = p_enabled and self._is_period_edit_mode
        self._period_from_input.setEnabled(fields_enabled)
        self._period_to_input.setEnabled(fields_enabled)
        self._period_amount_input.setEnabled(fields_enabled)
        self._period_note_input.setEnabled(fields_enabled)
        self._period_new_button.setEnabled(p_enabled and not self._is_period_edit_mode)
        self._period_edit_button.setEnabled(
            p_enabled and self._selected_period_id is not None and not self._is_period_edit_mode
        )
        self._period_save_button.setEnabled(p_enabled and self._is_period_edit_mode)
        self._period_delete_button.setEnabled(
            p_enabled and self._selected_period_id is not None and not self._is_period_edit_mode
        )

    def _set_primary_button(self, p_button: QPushButton) -> None:
        for button in (
            self._source_new_button,
            self._source_edit_button,
            self._source_save_button,
            self._period_new_button,
            self._period_edit_button,
            self._period_save_button,
        ):
            button.setDefault(False)
            button.setAutoDefault(False)
        p_button.setDefault(True)
        p_button.setAutoDefault(True)

    @staticmethod
    def _parse_amount(p_text: str) -> float:
        text = p_text.strip().replace(",", ".")
        if not text:
            raise DomainException("Betrag ist erforderlich.")
        try:
            value = float(text)
        except ValueError as exc:
            raise ValueError("Betrag muss numerisch sein.") from exc
        if value < 0:
            raise DomainException("Betrag darf nicht negativ sein.")
        return value
