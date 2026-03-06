from datetime import date

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.domain.exceptions import DomainException


APP_TITLE = "Mitarbeiterverwaltung"


class IncidentAnalystDialog(QDialog):
    def __init__(self, p_application, p_parent=None):
        super().__init__(p_parent)
        self._application = p_application
        self._selected_id: int | None = None
        self._is_edit_mode = False
        self._setup_ui()
        self._refresh_table()
        self._set_edit_fields_enabled(False)
        self._set_primary_action_button(self._new_button)

    def _setup_ui(self):
        self.setWindowTitle(APP_TITLE)
        self.resize(1180, 680)

        main_layout = QVBoxLayout()
        grid = QGridLayout()
        grid.setColumnStretch(0, 2)
        grid.setColumnStretch(1, 1)
        grid.setRowStretch(0, 1)

        display_group = QGroupBox("Anzeige")
        display_layout = QVBoxLayout()
        filter_layout = QHBoxLayout()
        self._filter_combo = QComboBox()
        self._filter_combo.addItems(["Alle", "Aktiv", "Inaktiv"])
        self._filter_combo.currentIndexChanged.connect(self._refresh_table)
        filter_layout.addWidget(self._filter_combo)
        filter_layout.addStretch()
        display_layout.addLayout(filter_layout)

        self._table = QTableWidget()
        self._table.setColumnCount(9)
        self._table.setHorizontalHeaderLabels(
            [
                "Buchungsname",
                "Typ",
                "Vorname",
                "Nachname",
                "E-Mail",
                "OpsGenie ID",
                "Standort",
                "Start",
                "Ende",
            ]
        )
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setSelectionMode(QTableWidget.SingleSelection)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.itemSelectionChanged.connect(self._on_row_selected)
        display_layout.addWidget(self._table)
        display_group.setLayout(display_layout)
        grid.addWidget(display_group, 0, 0)

        edit_group = QGroupBox("Edit")
        edit_layout = QVBoxLayout()

        # Block 1: Stammdaten
        stammdaten_group = QGroupBox("Stammdaten")
        stammdaten_layout = QGridLayout()
        self._vorname_input = QLineEdit()
        self._nachname_input = QLineEdit()
        self._email_input = QLineEdit()
        self._opsgenie_id_input = QLineEdit()
        self._vorname_input.setMinimumWidth(220)
        self._nachname_input.setMinimumWidth(220)
        self._email_input.setMinimumWidth(460)

        self._mitarbeitertyp_combo = QComboBox()
        self._mitarbeitertyp_combo.addItem("Incident Analyst", "INCIDENT_ANALYST")
        self._mitarbeitertyp_combo.addItem("Product Owner", "PRODUCT_OWNER")
        self._mitarbeitertyp_combo.addItem("Sonstige", "SONSTIGE")
        self._mitarbeitertyp_combo.setFocusPolicy(Qt.StrongFocus)

        self._location_combo = QComboBox()
        self._location_combo.setEditable(False)
        self._location_combo.setFocusPolicy(Qt.StrongFocus)

        stammdaten_layout.addWidget(QLabel("Vorname:"), 0, 0)
        stammdaten_layout.addWidget(self._vorname_input, 0, 1)
        stammdaten_layout.addWidget(QLabel("Nachname:"), 0, 2)
        stammdaten_layout.addWidget(self._nachname_input, 0, 3)
        stammdaten_layout.addWidget(QLabel("E-Mail:"), 1, 0)
        stammdaten_layout.addWidget(self._email_input, 1, 1, 1, 3)
        stammdaten_layout.addWidget(QLabel("Rolle:"), 2, 0)
        stammdaten_layout.addWidget(self._mitarbeitertyp_combo, 2, 1, 1, 3)
        stammdaten_layout.addWidget(QLabel("OpsGenie ID:"), 3, 0)
        stammdaten_layout.addWidget(self._opsgenie_id_input, 3, 1, 1, 3)
        stammdaten_layout.addWidget(QLabel("Standort:"), 4, 0)
        stammdaten_layout.addWidget(self._location_combo, 4, 1, 1, 3)
        stammdaten_layout.setColumnStretch(1, 1)
        stammdaten_layout.setColumnStretch(3, 1)
        stammdaten_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        stammdaten_group.setLayout(stammdaten_layout)
        edit_layout.addWidget(stammdaten_group)

        # Block 2: Aktivierung
        aktiv_group = QGroupBox("Aktivierung")
        aktiv_layout = QGridLayout()

        self._aktiv_checkbox = QCheckBox()
        self._aktiv_checkbox.setEnabled(False)
        self._aktiv_start_display = QLineEdit()
        self._aktiv_start_display.setReadOnly(True)
        self._aktiv_ende_display = QLineEdit()
        self._aktiv_ende_display.setReadOnly(True)

        aktiv_layout.addWidget(QLabel("Aktiv:"), 0, 0)
        aktiv_layout.addWidget(self._aktiv_checkbox, 0, 1)
        aktiv_layout.addWidget(QLabel("Seit:"), 1, 0)
        aktiv_layout.addWidget(self._aktiv_start_display, 1, 1)
        aktiv_layout.addWidget(QLabel("Bis:"), 1, 2)
        aktiv_layout.addWidget(self._aktiv_ende_display, 1, 3)

        aktiv_button_row = QHBoxLayout()
        self._activate_button = QPushButton("Aktivieren")
        self._activate_button.clicked.connect(self._on_activate_clicked)
        self._deactivate_button = QPushButton("Deaktivieren")
        self._deactivate_button.clicked.connect(self._on_deactivate_clicked)
        self._activation_history_button = QPushButton("Historie anzeigen")
        self._activation_history_button.clicked.connect(self._on_show_activation_history_clicked)
        aktiv_button_row.addWidget(self._activate_button)
        aktiv_button_row.addWidget(self._deactivate_button)
        aktiv_button_row.addWidget(self._activation_history_button)
        aktiv_button_row.addStretch()
        aktiv_layout.addWidget(self._wrap_layout(aktiv_button_row), 2, 0, 1, 4)
        aktiv_layout.setColumnStretch(1, 1)
        aktiv_layout.setColumnStretch(3, 1)
        aktiv_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        aktiv_group.setLayout(aktiv_layout)
        edit_layout.addWidget(aktiv_group)

        # Block 3: Gehaltsgruppe
        gehaltsgruppe_group = QGroupBox("Gehaltsgruppenzuordnung")
        gehaltsgruppe_layout = QGridLayout()

        self._salary_group_display = QLineEdit()
        self._salary_group_display.setReadOnly(True)
        self._salary_from_display = QLineEdit()
        self._salary_from_display.setReadOnly(True)
        self._salary_to_display = QLineEdit()
        self._salary_to_display.setReadOnly(True)

        gehaltsgruppe_layout.addWidget(QLabel("Gehaltsgruppe:"), 0, 0)
        gehaltsgruppe_layout.addWidget(self._salary_group_display, 0, 1, 1, 3)
        gehaltsgruppe_layout.addWidget(QLabel("Seit:"), 1, 0)
        gehaltsgruppe_layout.addWidget(self._salary_from_display, 1, 1)
        gehaltsgruppe_layout.addWidget(QLabel("Bis:"), 1, 2)
        gehaltsgruppe_layout.addWidget(self._salary_to_display, 1, 3)

        salary_button_row = QHBoxLayout()
        self._assign_or_change_salary_group_button = QPushButton("Gehaltsgruppe zuweisen")
        self._assign_or_change_salary_group_button.clicked.connect(
            self._on_assign_or_change_salary_group_clicked
        )
        self._correct_salary_group_button = QPushButton("Gehaltsgruppe korrigieren")
        self._correct_salary_group_button.clicked.connect(self._on_correct_salary_group_clicked)
        self._salary_history_button = QPushButton("Historie anzeigen")
        self._salary_history_button.clicked.connect(self._on_show_salary_history_clicked)
        salary_button_row.addWidget(self._assign_or_change_salary_group_button)
        salary_button_row.addWidget(self._correct_salary_group_button)
        salary_button_row.addWidget(self._salary_history_button)
        salary_button_row.addStretch()
        gehaltsgruppe_layout.addWidget(self._wrap_layout(salary_button_row), 2, 0, 1, 4)
        gehaltsgruppe_layout.setColumnStretch(1, 1)
        gehaltsgruppe_layout.setColumnStretch(3, 1)
        gehaltsgruppe_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        gehaltsgruppe_group.setLayout(gehaltsgruppe_layout)
        edit_layout.addWidget(gehaltsgruppe_group)

        edit_group.setLayout(edit_layout)
        grid.addWidget(edit_group, 0, 1)

        # Untere Aktionen
        buttons1_group = QWidget()
        buttons1_layout = QHBoxLayout()
        buttons1_layout.setContentsMargins(0, 0, 0, 0)
        self._new_button = QPushButton("Neu")
        self._new_button.clicked.connect(self._on_new_clicked)
        self._edit_button = QPushButton("Bearbeiten")
        self._edit_button.clicked.connect(self._on_edit_clicked)
        self._save_button = QPushButton("Speichern")
        self._save_button.clicked.connect(self._on_save_clicked)
        self._delete_button = QPushButton("Löschen")
        self._delete_button.clicked.connect(self._on_delete_clicked)
        buttons1_layout.addWidget(self._new_button)
        buttons1_layout.addWidget(self._edit_button)
        buttons1_layout.addWidget(self._save_button)
        buttons1_layout.addWidget(self._delete_button)
        buttons1_layout.addStretch()
        buttons1_group.setLayout(buttons1_layout)
        grid.addWidget(buttons1_group, 1, 0)

        buttons2_group = QWidget()
        buttons2_layout = QHBoxLayout()
        buttons2_layout.setContentsMargins(0, 0, 0, 0)
        self._close_button = QPushButton("Dialog schließen")
        self._close_button.clicked.connect(self.close)
        buttons2_layout.addStretch()
        buttons2_layout.addWidget(self._close_button)
        buttons2_group.setLayout(buttons2_layout)
        grid.addWidget(buttons2_group, 1, 1)

        main_layout.addLayout(grid)
        self.setLayout(main_layout)
        self._configure_tab_order()

    def _configure_tab_order(self) -> None:
        QWidget.setTabOrder(self._vorname_input, self._nachname_input)
        QWidget.setTabOrder(self._nachname_input, self._email_input)
        QWidget.setTabOrder(self._email_input, self._mitarbeitertyp_combo)
        QWidget.setTabOrder(self._mitarbeitertyp_combo, self._opsgenie_id_input)
        QWidget.setTabOrder(self._opsgenie_id_input, self._location_combo)
        QWidget.setTabOrder(self._location_combo, self._activate_button)
        QWidget.setTabOrder(self._activate_button, self._deactivate_button)
        QWidget.setTabOrder(self._deactivate_button, self._activation_history_button)
        QWidget.setTabOrder(
            self._activation_history_button, self._assign_or_change_salary_group_button
        )
        QWidget.setTabOrder(
            self._assign_or_change_salary_group_button, self._correct_salary_group_button
        )
        QWidget.setTabOrder(self._correct_salary_group_button, self._salary_history_button)
        QWidget.setTabOrder(self._salary_history_button, self._save_button)

    def _wrap_layout(self, p_layout: QHBoxLayout) -> QWidget:
        widget = QWidget()
        widget.setLayout(p_layout)
        return widget

    def _refresh_table(self):
        analysts = self._application.get_all_incident_analysts()
        filter_value = self._filter_combo.currentText()
        filtered = []
        for analyst in analysts:
            if filter_value == "Aktiv" and not analyst.is_active:
                continue
            if filter_value == "Inaktiv" and analyst.is_active:
                continue
            filtered.append(analyst)

        self._table.setRowCount(len(filtered))
        for row_index, analyst in enumerate(filtered):
            row_items = [
                analyst.buchungsname,
                self._display_mitarbeitertyp(analyst.mitarbeitertyp),
                analyst.vornamen,
                analyst.nachname,
                analyst.email,
                analyst.opsgenie_id or "",
                analyst.oncall_location_id,
                self._format_date(analyst.start_datum),
                self._format_date(analyst.ende_datum),
            ]
            for col, text in enumerate(row_items):
                item = QTableWidgetItem(text)
                item.setData(Qt.UserRole, analyst.id)
                if not analyst.is_active:
                    item.setForeground(Qt.gray)
                self._table.setItem(row_index, col, item)

        self._table.resizeColumnsToContents()

    def _load_oncall_locations(self):
        current = self._location_combo.currentText()
        self._location_combo.clear()
        locations = self._application.get_oncall_locations()
        for location in locations:
            self._location_combo.addItem(location["id"])

        if self._location_combo.count() == 0:
            self._location_combo.addItem("GER")

        preferred = current or "GER"
        idx = self._location_combo.findText(preferred)
        if idx < 0:
            self._location_combo.addItem(preferred)
            idx = self._location_combo.findText(preferred)
        self._location_combo.setCurrentIndex(max(idx, 0))

    def _clear_form(self):
        self._selected_id = None
        self._is_edit_mode = False

        self._vorname_input.clear()
        self._nachname_input.clear()
        self._email_input.clear()
        self._opsgenie_id_input.clear()

        idx = self._mitarbeitertyp_combo.findData("INCIDENT_ANALYST")
        self._mitarbeitertyp_combo.setCurrentIndex(max(idx, 0))
        self._load_oncall_locations()

        self._aktiv_checkbox.setChecked(False)
        self._aktiv_start_display.clear()
        self._aktiv_ende_display.clear()

        self._salary_group_display.clear()
        self._salary_from_display.clear()
        self._salary_to_display.clear()

        self._table.blockSignals(True)
        self._table.clearSelection()
        self._table.setCurrentCell(-1, -1)
        self._table.blockSignals(False)

        self._refresh_activation_block([])
        self._refresh_salary_block([], None)
        self._set_primary_action_button(self._new_button)

    def _set_edit_fields_enabled(self, p_enabled: bool):
        self._vorname_input.setEnabled(p_enabled)
        self._nachname_input.setEnabled(p_enabled)
        self._email_input.setEnabled(p_enabled)
        self._opsgenie_id_input.setEnabled(p_enabled)
        self._mitarbeitertyp_combo.setEnabled(p_enabled)
        self._location_combo.setEnabled(p_enabled)

    def _set_primary_action_button(self, p_button: QPushButton):
        for button in (self._new_button, self._edit_button, self._save_button):
            button.setDefault(False)
            button.setAutoDefault(False)
        p_button.setAutoDefault(True)
        p_button.setDefault(True)

    def _format_date(self, p_date: date | None) -> str:
        if p_date is None:
            return ""
        return p_date.strftime("%d.%m.%y")

    def _format_iso_date_text(self, p_text: str | None) -> str:
        if p_text is None:
            return ""
        text = str(p_text).strip()
        if text == "":
            return ""
        return date.fromisoformat(text).strftime("%d.%m.%y")

    def _get_selected_analyst(self):
        if self._selected_id is None:
            return None
        for analyst in self._application.get_all_incident_analysts():
            if analyst.id == self._selected_id:
                return analyst
        return None

    def _on_row_selected(self):
        row = self._table.currentRow()
        if row < 0:
            return

        item = self._table.item(row, 0)
        if item is None:
            return

        analyst_id = item.data(Qt.UserRole)
        if analyst_id is None:
            return

        self._selected_id = int(analyst_id)
        analyst = self._get_selected_analyst()
        if analyst is None:
            return

        self._vorname_input.setText(analyst.vornamen)
        self._nachname_input.setText(analyst.nachname)
        self._email_input.setText(analyst.email)
        self._opsgenie_id_input.setText(analyst.opsgenie_id or "")

        type_index = self._mitarbeitertyp_combo.findData(analyst.mitarbeitertyp)
        self._mitarbeitertyp_combo.setCurrentIndex(max(type_index, 0))

        self._load_oncall_locations()
        loc_idx = self._location_combo.findText(analyst.oncall_location_id)
        if loc_idx < 0:
            self._location_combo.addItem(analyst.oncall_location_id)
            loc_idx = self._location_combo.findText(analyst.oncall_location_id)
        self._location_combo.setCurrentIndex(max(loc_idx, 0))

        activation_periods = self._application.get_activation_periods_for_mitarbeiter(analyst.id)
        current_period = self._application.get_current_activation_period_for_mitarbeiter(analyst.id)
        self._refresh_activation_block(activation_periods, current_period)

        assignments = self._application.get_gehaltsgruppen_assignments_for_mitarbeiter(analyst.id)
        current_assignment = self._application.get_gehaltsgruppe_assignment_for_mitarbeiter_at(
            p_mitarbeiter_id=analyst.id,
            p_stichtag=date.today(),
        )
        self._refresh_salary_block(assignments, current_assignment)

        self._is_edit_mode = False
        self._set_edit_fields_enabled(False)
        self._set_primary_action_button(self._edit_button)

    def _refresh_activation_block(
        self,
        p_periods: list[dict[str, str | int]],
        p_current_period: dict[str, str | int] | None = None,
    ) -> None:
        current = p_current_period
        if current is None and len(p_periods) > 0:
            current = p_periods[-1]

        if current is None:
            self._aktiv_checkbox.setChecked(False)
            self._aktiv_start_display.clear()
            self._aktiv_ende_display.clear()
            has_open_period = False
        else:
            start_text = str(current.get("start_datum", "")).strip()
            end_text = str(current.get("ende_datum", "")).strip()
            self._aktiv_checkbox.setChecked(start_text != "" and end_text == "")
            self._aktiv_start_display.setText(self._format_iso_date_text(start_text))
            self._aktiv_ende_display.setText(self._format_iso_date_text(end_text))
            has_open_period = end_text == ""

        has_selection = self._selected_id is not None
        self._activate_button.setEnabled(has_selection and not has_open_period)
        self._deactivate_button.setEnabled(has_selection and has_open_period)
        self._activation_history_button.setEnabled(has_selection and len(p_periods) > 1)

    def _refresh_salary_block(
        self,
        p_assignments: list[dict[str, str | int]],
        p_current_assignment: dict[str, str | int] | None,
    ) -> None:
        has_selection = self._selected_id is not None
        has_assignment = p_current_assignment is not None

        if not has_assignment:
            self._salary_group_display.clear()
            self._salary_from_display.clear()
            self._salary_to_display.clear()
            self._assign_or_change_salary_group_button.setText("Gehaltsgruppe zuweisen")
        else:
            self._salary_group_display.setText(
                str(p_current_assignment.get("gehaltsgruppe_bezeichnung", ""))
            )
            self._salary_from_display.setText(
                self._format_iso_date_text(str(p_current_assignment.get("gueltig_ab", "")))
            )
            self._salary_to_display.setText(
                self._format_iso_date_text(str(p_current_assignment.get("gueltig_bis", "")))
            )
            self._assign_or_change_salary_group_button.setText("Gehaltsgruppe ändern")

        self._assign_or_change_salary_group_button.setEnabled(has_selection)
        self._correct_salary_group_button.setEnabled(has_selection and has_assignment)
        self._salary_history_button.setEnabled(has_selection and len(p_assignments) > 1)

    def _on_new_clicked(self):
        self._clear_form()
        self._is_edit_mode = False
        self._set_edit_fields_enabled(True)
        self._activate_button.setEnabled(True)
        self._deactivate_button.setEnabled(False)
        self._activation_history_button.setEnabled(False)
        self._assign_or_change_salary_group_button.setEnabled(True)
        self._correct_salary_group_button.setEnabled(False)
        self._salary_history_button.setEnabled(False)
        self._vorname_input.setFocus()

    def _on_edit_clicked(self):
        if self._selected_id is None:
            QMessageBox.information(self, APP_TITLE, "Bitte zuerst einen Eintrag auswählen.")
            return
        self._is_edit_mode = True
        self._set_edit_fields_enabled(True)
        self._vorname_input.setFocus()
        self._set_primary_action_button(self._save_button)

    def _on_save_clicked(self):
        try:
            if self._is_edit_mode:
                if self._selected_id is None:
                    QMessageBox.information(self, APP_TITLE, "Bitte zuerst einen Eintrag auswählen.")
                    return

                existing = self._get_selected_analyst()
                if existing is None:
                    QMessageBox.warning(self, APP_TITLE, "Mitarbeiter nicht gefunden.")
                    return

                self._application.update_incident_analyst(
                    p_id=self._selected_id,
                    p_vornamen=self._vorname_input.text(),
                    p_nachname=self._nachname_input.text(),
                    p_email=self._email_input.text(),
                    p_start_datum=existing.start_datum,
                    p_ende_datum=existing.ende_datum,
                    p_opsgenie_id=self._opsgenie_id_input.text().strip() or None,
                    p_oncall_location_id=self._location_combo.currentText(),
                    p_mitarbeitertyp=str(self._mitarbeitertyp_combo.currentData()),
                )
                selected_id = self._selected_id
            else:
                saved = self._application.add_incident_analyst(
                    p_vornamen=self._vorname_input.text(),
                    p_nachname=self._nachname_input.text(),
                    p_email=self._email_input.text(),
                    p_start_datum=date.today(),
                    p_ende_datum=None,
                    p_oncall_location_id=self._location_combo.currentText(),
                    p_mitarbeitertyp=str(self._mitarbeitertyp_combo.currentData()),
                )
                selected_id = int(saved.id)

        except DomainException as e:
            QMessageBox.warning(self, APP_TITLE, str(e))
            return
        except Exception as e:
            QMessageBox.warning(self, APP_TITLE, str(e))
            return

        self._refresh_table_and_reload_selected(selected_id)
        self._set_edit_fields_enabled(False)
        self._is_edit_mode = False

    def _on_delete_clicked(self):
        if self._selected_id is None:
            QMessageBox.information(self, APP_TITLE, "Bitte zuerst einen Eintrag auswählen.")
            return

        confirmation = QMessageBox(self)
        confirmation.setWindowTitle(APP_TITLE)
        confirmation.setText("Ausgewaehlten Mitarbeiter wirklich loeschen?")
        confirmation.setIcon(QMessageBox.Question)
        yes_button = confirmation.addButton("Ja", QMessageBox.YesRole)
        no_button = confirmation.addButton("Nein", QMessageBox.NoRole)
        confirmation.setDefaultButton(no_button)
        confirmation.exec()

        if confirmation.clickedButton() is not yes_button:
            return

        self._application.delete_incident_analyst(self._selected_id)
        self._refresh_table()
        self._clear_form()
        self._set_edit_fields_enabled(False)

    def _display_mitarbeitertyp(self, p_type: str) -> str:
        mapping = {
            "INCIDENT_ANALYST": "Incident Analyst",
            "PRODUCT_OWNER": "Product Owner",
            "SONSTIGE": "Sonstige",
        }
        return mapping.get((p_type or "").strip().upper(), str(p_type))

    def _select_row_by_id(self, p_analyst_id: int | None) -> None:
        if p_analyst_id is None:
            return
        for row in range(self._table.rowCount()):
            item = self._table.item(row, 0)
            if item is None:
                continue
            if int(item.data(Qt.UserRole)) == int(p_analyst_id):
                self._table.selectRow(row)
                self._table.setCurrentCell(row, 0)
                return

    def _refresh_table_and_reload_selected(self, p_analyst_id: int | None) -> None:
        self._refresh_table()
        self._select_row_by_id(p_analyst_id)
        if p_analyst_id is None:
            return
        selected_row = self._table.currentRow()
        if selected_row < 0:
            return
        self._selected_id = int(p_analyst_id)
        self._on_row_selected()

    def _open_date_input_dialog(self, p_title: str, p_label: str, p_default: date) -> date | None:
        dialog = QDialog(self)
        dialog.setWindowTitle(p_title)
        layout = QFormLayout(dialog)

        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDisplayFormat("dd.MM.yy")
        date_edit.setDate(QDate(p_default.year, p_default.month, p_default.day))
        layout.addRow(p_label, date_edit)

        buttons = QDialogButtonBox()
        ok_button = buttons.addButton("OK", QDialogButtonBox.AcceptRole)
        cancel_button = buttons.addButton("Abbrechen", QDialogButtonBox.RejectRole)
        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        layout.addRow(buttons)

        if dialog.exec() != QDialog.Accepted:
            return None

        picked = date_edit.date()
        return date(picked.year(), picked.month(), picked.day())

    def _on_activate_clicked(self):
        if self._selected_id is None:
            if not self._create_new_mitarbeiter_from_form_for_follow_up():
                return

        start_date = self._open_date_input_dialog(
            p_title="Mitarbeiter aktivieren",
            p_label="Startdatum:",
            p_default=date.today(),
        )
        if start_date is None:
            return

        try:
            self._application.activate_mitarbeiter(
                p_mitarbeiter_id=self._selected_id,
                p_start_datum=start_date,
            )
        except DomainException as e:
            QMessageBox.warning(self, APP_TITLE, str(e))
            return
        except Exception as e:
            QMessageBox.warning(self, APP_TITLE, str(e))
            return

        selected_id = self._selected_id
        self._refresh_table_and_reload_selected(selected_id)

    def _on_deactivate_clicked(self):
        if self._selected_id is None:
            QMessageBox.information(self, APP_TITLE, "Bitte zuerst einen Eintrag auswählen.")
            return

        end_date = self._open_date_input_dialog(
            p_title="Mitarbeiter deaktivieren",
            p_label="Enddatum:",
            p_default=date.today(),
        )
        if end_date is None:
            return

        try:
            self._application.deactivate_mitarbeiter(
                p_mitarbeiter_id=self._selected_id,
                p_ende_datum=end_date,
            )
        except DomainException as e:
            QMessageBox.warning(self, APP_TITLE, str(e))
            return
        except Exception as e:
            QMessageBox.warning(self, APP_TITLE, str(e))
            return

        selected_id = self._selected_id
        self._refresh_table_and_reload_selected(selected_id)

    def _on_show_activation_history_clicked(self):
        if self._selected_id is None:
            return
        periods = self._application.get_activation_periods_for_mitarbeiter(self._selected_id)
        self._show_activation_history_dialog(periods)

    def _show_activation_history_dialog(self, p_periods: list[dict[str, str | int]]) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Aktivierungshistorie")
        dialog.resize(480, 280)

        layout = QVBoxLayout(dialog)
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Start", "Ende"])
        table.setRowCount(len(p_periods))

        for row, period in enumerate(p_periods):
            start_item = QTableWidgetItem(
                self._format_iso_date_text(str(period.get("start_datum", "")))
            )
            end_item = QTableWidgetItem(
                self._format_iso_date_text(str(period.get("ende_datum", "")))
            )
            table.setItem(row, 0, start_item)
            table.setItem(row, 1, end_item)

        table.resizeColumnsToContents()
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(table)

        buttons = QDialogButtonBox()
        close_button = buttons.addButton("Schließen", QDialogButtonBox.RejectRole)
        close_button.clicked.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.exec()

    def _open_salary_assignment_dialog(
        self,
        p_title: str,
        p_allow_start_change: bool,
        p_current_assignment: dict[str, str | int] | None,
        p_oncall_location_id: str | None = None,
    ) -> tuple[int, date] | None:
        normalized_location = (p_oncall_location_id or "").strip().upper()
        all_groups = self._application.get_gehaltsgruppen()
        groups = [
            group
            for group in all_groups
            if normalized_location == ""
            or getattr(group, "oncall_location_id", "").strip().upper() == normalized_location
        ]

        if normalized_location == "":
            QMessageBox.warning(self, APP_TITLE, "Mitarbeiterstandort konnte nicht ermittelt werden.")
            return None

        if not groups:
            QMessageBox.information(
                self,
                APP_TITLE,
                f"Keine Gehaltsgruppen für Standort {normalized_location} vorhanden.",
            )
            return None

        dialog = QDialog(self)
        dialog.setWindowTitle(p_title)
        layout = QFormLayout(dialog)

        group_combo = QComboBox()
        for group in groups:
            group_combo.addItem(str(group.bezeichnung), int(group.id))

        if p_current_assignment is not None:
            current_group_id = int(p_current_assignment.get("gehaltsgruppe_id", 0))
            index = group_combo.findData(current_group_id)
            if index >= 0:
                group_combo.setCurrentIndex(index)

        layout.addRow("Gehaltsgruppe:", group_combo)

        fixed_start_date: date | None = None
        date_edit: QDateEdit | None = None

        if p_allow_start_change:
            default_date = date.today()
            date_edit = QDateEdit()
            date_edit.setCalendarPopup(True)
            date_edit.setDisplayFormat("dd.MM.yy")
            date_edit.setDate(QDate(default_date.year, default_date.month, default_date.day))
            layout.addRow("Gueltig ab:", date_edit)
        else:
            if p_current_assignment is None:
                return None
            fixed_start_date = date.fromisoformat(str(p_current_assignment["gueltig_ab"]))
            fixed_start_input = QLineEdit(self._format_date(fixed_start_date))
            fixed_start_input.setReadOnly(True)
            layout.addRow("Gueltig ab:", fixed_start_input)

        buttons = QDialogButtonBox()
        ok_button = buttons.addButton("OK", QDialogButtonBox.AcceptRole)
        cancel_button = buttons.addButton("Abbrechen", QDialogButtonBox.RejectRole)
        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        layout.addRow(buttons)

        if dialog.exec() != QDialog.Accepted:
            return None

        selected_group_id = int(group_combo.currentData())
        if p_allow_start_change:
            assert date_edit is not None
            picked = date_edit.date()
            valid_from = date(picked.year(), picked.month(), picked.day())
        else:
            assert fixed_start_date is not None
            valid_from = fixed_start_date

        return selected_group_id, valid_from

    def _on_assign_or_change_salary_group_clicked(self):
        if self._selected_id is None:
            if not self._create_new_mitarbeiter_from_form_for_follow_up():
                return

        current_assignment = self._application.get_gehaltsgruppe_assignment_for_mitarbeiter_at(
            p_mitarbeiter_id=self._selected_id,
            p_stichtag=date.today(),
        )
        title = (
            "Gehaltsgruppe zuweisen"
            if current_assignment is None
            else "Gehaltsgruppe ändern"
        )
        analyst = self._get_selected_analyst()
        if analyst is None:
            QMessageBox.warning(self, APP_TITLE, "Mitarbeiter nicht gefunden.")
            return

        result = self._open_salary_assignment_dialog(
            p_title=title,
            p_allow_start_change=True,
            p_current_assignment=current_assignment,
            p_oncall_location_id=analyst.oncall_location_id,
        )
        if result is None:
            return

        gehaltsgruppe_id, gueltig_ab = result
        try:
            self._application.assign_gehaltsgruppe_to_mitarbeiter(
                p_mitarbeiter_id=self._selected_id,
                p_gehaltsgruppe_id=gehaltsgruppe_id,
                p_gueltig_ab=gueltig_ab,
                p_gueltig_bis=None,
            )
        except DomainException as e:
            QMessageBox.warning(self, APP_TITLE, str(e))
            return
        except Exception as e:
            QMessageBox.warning(self, APP_TITLE, str(e))
            return

        selected_id = self._selected_id
        self._refresh_table_and_reload_selected(selected_id)

    def _create_new_mitarbeiter_from_form_for_follow_up(self) -> bool:
        existing_id = self._find_mitarbeiter_id_by_email(self._email_input.text())
        if existing_id is not None:
            self._selected_id = int(existing_id)
            self._is_edit_mode = False
            self._set_edit_fields_enabled(False)
            self._refresh_table()
            self._select_row_by_id(self._selected_id)
            return True

        try:
            saved = self._application.add_incident_analyst(
                p_vornamen=self._vorname_input.text(),
                p_nachname=self._nachname_input.text(),
                p_email=self._email_input.text(),
                p_start_datum=date.today(),
                p_ende_datum=None,
                p_oncall_location_id=self._location_combo.currentText(),
                p_mitarbeitertyp=str(self._mitarbeitertyp_combo.currentData()),
            )
        except DomainException as e:
            QMessageBox.warning(self, APP_TITLE, str(e))
            return False
        except Exception as e:
            QMessageBox.warning(self, APP_TITLE, str(e))
            return False

        self._selected_id = int(saved.id)
        self._refresh_table_and_reload_selected(self._selected_id)
        self._is_edit_mode = False
        self._set_edit_fields_enabled(False)
        return self._selected_id is not None

    def _find_mitarbeiter_id_by_email(self, p_email: str) -> int | None:
        email = p_email.strip().lower()
        if email == "":
            return None
        for analyst in self._application.get_all_incident_analysts():
            if analyst.email.strip().lower() == email:
                return int(analyst.id)
        return None

    def _on_correct_salary_group_clicked(self):
        if self._selected_id is None:
            QMessageBox.information(self, APP_TITLE, "Bitte zuerst einen Eintrag auswählen.")
            return

        current_assignment = self._application.get_gehaltsgruppe_assignment_for_mitarbeiter_at(
            p_mitarbeiter_id=self._selected_id,
            p_stichtag=date.today(),
        )
        if current_assignment is None:
            QMessageBox.information(
                self,
                APP_TITLE,
                "Es ist keine Gehaltsgruppe zur Korrektur vorhanden.",
            )
            return

        result = self._open_salary_assignment_dialog(
            p_title="Gehaltsgruppe korrigieren",
            p_allow_start_change=False,
            p_current_assignment=current_assignment,
            p_oncall_location_id=analyst.oncall_location_id if (analyst := self._get_selected_analyst()) else None,
        )
        if result is None:
            return

        gehaltsgruppe_id, gueltig_ab = result
        gueltig_bis_text = str(current_assignment.get("gueltig_bis", "")).strip()
        gueltig_bis = date.fromisoformat(gueltig_bis_text) if gueltig_bis_text else None

        try:
            self._application.assign_gehaltsgruppe_to_mitarbeiter(
                p_mitarbeiter_id=self._selected_id,
                p_gehaltsgruppe_id=gehaltsgruppe_id,
                p_gueltig_ab=gueltig_ab,
                p_gueltig_bis=gueltig_bis,
            )
        except DomainException as e:
            QMessageBox.warning(self, APP_TITLE, str(e))
            return
        except Exception as e:
            QMessageBox.warning(self, APP_TITLE, str(e))
            return

        selected_id = self._selected_id
        self._refresh_table_and_reload_selected(selected_id)

    def _on_show_salary_history_clicked(self):
        if self._selected_id is None:
            return
        assignments = self._application.get_gehaltsgruppen_assignments_for_mitarbeiter(self._selected_id)
        self._show_salary_history_dialog(assignments)

    def _show_salary_history_dialog(self, p_assignments: list[dict[str, str | int]]) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Gehaltsgruppenhistorie")
        dialog.resize(640, 320)

        layout = QVBoxLayout(dialog)
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Gehaltsgruppe", "Gueltig ab", "Gueltig bis"])
        table.setRowCount(len(p_assignments))

        for row, assignment in enumerate(p_assignments):
            group_item = QTableWidgetItem(str(assignment.get("gehaltsgruppe_bezeichnung", "")))
            start_item = QTableWidgetItem(
                self._format_iso_date_text(str(assignment.get("gueltig_ab", "")))
            )
            end_item = QTableWidgetItem(
                self._format_iso_date_text(str(assignment.get("gueltig_bis", "")))
            )
            table.setItem(row, 0, group_item)
            table.setItem(row, 1, start_item)
            table.setItem(row, 2, end_item)

        table.resizeColumnsToContents()
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(table)

        buttons = QDialogButtonBox()
        close_button = buttons.addButton("Schließen", QDialogButtonBox.RejectRole)
        close_button.clicked.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.exec()
