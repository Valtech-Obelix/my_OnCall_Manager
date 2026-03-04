from datetime import date

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.domain.exceptions import DomainException


APP_TITLE = "Verwaltung der Incident Analysten"


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
        self.resize(1080, 600)

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
        self._table.setColumnCount(8)
        self._table.setHorizontalHeaderLabels(
            [
                "Buchungsname",
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
        edit_layout = QFormLayout()
        self._vorname_input = QLineEdit()
        self._nachname_input = QLineEdit()
        self._email_input = QLineEdit()
        self._opsgenie_id_input = QLineEdit()
        self._location_combo = QComboBox()
        self._location_combo.setEditable(False)
        self._start_input = QDateEdit()
        self._start_input.setCalendarPopup(True)
        self._end_enabled_checkbox = QCheckBox("Enddatum gesetzt")
        self._end_enabled_checkbox.toggled.connect(self._toggle_end_enabled)
        self._end_input = QDateEdit()
        self._end_input.setCalendarPopup(True)

        edit_layout.addRow("Vorname:", self._vorname_input)
        edit_layout.addRow("Nachname:", self._nachname_input)
        edit_layout.addRow("E-Mail:", self._email_input)
        edit_layout.addRow("OpsGenie ID:", self._opsgenie_id_input)
        edit_layout.addRow("Standort:", self._location_combo)
        edit_layout.addRow("Startdatum:", self._start_input)
        edit_layout.addRow("", self._end_enabled_checkbox)
        edit_layout.addRow("Enddatum:", self._end_input)
        edit_group.setLayout(edit_layout)
        grid.addWidget(edit_group, 0, 1)

        buttons1_group = QWidget()
        buttons1_layout = QHBoxLayout()
        buttons1_layout.setContentsMargins(0, 0, 0, 0)
        self._new_button = QPushButton("Neu")
        self._new_button.clicked.connect(self._on_new_clicked)
        self._edit_button = QPushButton("Bearbeiten")
        self._edit_button.clicked.connect(self._on_edit_clicked)
        self._save_button = QPushButton("Speichern")
        self._save_button.clicked.connect(self._on_save_clicked)
        self._deactivate_button = QPushButton("Deaktivieren")
        self._deactivate_button.clicked.connect(self._on_deactivate_clicked)
        self._delete_button = QPushButton("Löschen")
        self._delete_button.clicked.connect(self._on_delete_clicked)
        buttons1_layout.addWidget(self._new_button)
        buttons1_layout.addWidget(self._edit_button)
        buttons1_layout.addWidget(self._save_button)
        buttons1_layout.addWidget(self._deactivate_button)
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
                analyst.vornamen,
                analyst.nachname,
                analyst.email,
                analyst.opsgenie_id or "",
                analyst.oncall_location_id,
                analyst.start_datum.isoformat(),
                analyst.ende_datum.isoformat() if analyst.ende_datum else "",
            ]
            for col, text in enumerate(row_items):
                item = QTableWidgetItem(text)
                item.setData(Qt.UserRole, analyst.id)
                if not analyst.is_active:
                    item.setForeground(Qt.gray)
                self._table.setItem(row_index, col, item)
        self._table.resizeColumnsToContents()
        self._table.clearSelection()
        self._selected_id = None
        self._set_primary_action_button(self._new_button)

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
        self._load_oncall_locations()
        self._start_input.setDate(QDate.currentDate())
        self._end_enabled_checkbox.setChecked(False)
        self._end_input.setDate(QDate.currentDate())
        self._table.clearSelection()
        self._set_primary_action_button(self._new_button)

    def _set_edit_fields_enabled(self, p_enabled: bool):
        self._vorname_input.setEnabled(p_enabled)
        self._nachname_input.setEnabled(p_enabled)
        self._email_input.setEnabled(p_enabled)
        self._opsgenie_id_input.setEnabled(p_enabled)
        self._location_combo.setEnabled(p_enabled)
        self._start_input.setEnabled(p_enabled)
        self._end_enabled_checkbox.setEnabled(p_enabled)
        self._end_input.setEnabled(p_enabled and self._end_enabled_checkbox.isChecked())

    def _set_primary_action_button(self, p_button: QPushButton):
        for button in (self._new_button, self._edit_button, self._save_button):
            button.setDefault(False)
            button.setAutoDefault(False)
        p_button.setAutoDefault(True)
        p_button.setDefault(True)

    def _toggle_end_enabled(self, p_checked: bool):
        self._end_input.setEnabled(self._end_enabled_checkbox.isEnabled() and p_checked)

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
        self._load_oncall_locations()
        loc_idx = self._location_combo.findText(analyst.oncall_location_id)
        if loc_idx < 0:
            self._location_combo.addItem(analyst.oncall_location_id)
            loc_idx = self._location_combo.findText(analyst.oncall_location_id)
        self._location_combo.setCurrentIndex(max(loc_idx, 0))
        self._start_input.setDate(
            QDate(
                analyst.start_datum.year,
                analyst.start_datum.month,
                analyst.start_datum.day,
            )
        )
        if analyst.ende_datum:
            self._end_enabled_checkbox.setChecked(True)
            self._end_input.setDate(
                QDate(
                    analyst.ende_datum.year,
                    analyst.ende_datum.month,
                    analyst.ende_datum.day,
                )
            )
        else:
            self._end_enabled_checkbox.setChecked(False)
            self._end_input.setDate(QDate.currentDate())

        self._set_edit_fields_enabled(False)
        self._set_primary_action_button(self._edit_button)

    def _on_new_clicked(self):
        self._clear_form()
        self._is_edit_mode = False
        self._set_edit_fields_enabled(True)
        self._vorname_input.setFocus()

    def _on_edit_clicked(self):
        if self._selected_id is None:
            QMessageBox.information(self, APP_TITLE, "Bitte zuerst einen Eintrag auswählen.")
            return
        self._is_edit_mode = True
        self._set_edit_fields_enabled(True)
        self._vorname_input.setFocus()
        self._set_primary_action_button(self._edit_button)

    def _on_save_clicked(self):
        start_qdate = self._start_input.date()
        start_date = date(start_qdate.year(), start_qdate.month(), start_qdate.day())

        end_date = None
        if self._end_enabled_checkbox.isChecked():
            end_qdate = self._end_input.date()
            end_date = date(end_qdate.year(), end_qdate.month(), end_qdate.day())

        try:
            if self._is_edit_mode:
                if self._selected_id is None:
                    QMessageBox.information(self, APP_TITLE, "Bitte zuerst einen Eintrag auswählen.")
                    return
                self._application.update_incident_analyst(
                    p_id=self._selected_id,
                    p_vornamen=self._vorname_input.text(),
                    p_nachname=self._nachname_input.text(),
                    p_email=self._email_input.text(),
                    p_start_datum=start_date,
                    p_ende_datum=end_date,
                    p_opsgenie_id=self._opsgenie_id_input.text().strip() or None,
                    p_oncall_location_id=self._location_combo.currentText(),
                )
            else:
                self._application.add_incident_analyst(
                    p_vornamen=self._vorname_input.text(),
                    p_nachname=self._nachname_input.text(),
                    p_email=self._email_input.text(),
                    p_start_datum=start_date,
                    p_ende_datum=end_date,
                    p_oncall_location_id=self._location_combo.currentText(),
                )
        except DomainException as e:
            QMessageBox.warning(self, APP_TITLE, str(e))
            return
        except Exception as e:
            QMessageBox.warning(self, APP_TITLE, str(e))
            return

        self._refresh_table()
        self._clear_form()
        self._set_edit_fields_enabled(False)

    def _on_delete_clicked(self):
        if self._selected_id is None:
            QMessageBox.information(self, APP_TITLE, "Bitte zuerst einen Eintrag auswählen.")
            return

        reply = QMessageBox.question(
            self,
            APP_TITLE,
            "Ausgewählten Incident Analyst wirklich löschen?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        self._application.delete_incident_analyst(self._selected_id)
        self._refresh_table()
        self._clear_form()
        self._set_edit_fields_enabled(False)

    def _on_deactivate_clicked(self):
        if self._selected_id is None:
            QMessageBox.information(self, APP_TITLE, "Bitte zuerst einen Eintrag auswählen.")
            return

        ende_qdate = QDate.currentDate()
        if self._end_enabled_checkbox.isChecked():
            ende_qdate = self._end_input.date()

        try:
            self._application.deactivate_incident_analyst(
                self._selected_id,
                date(ende_qdate.year(), ende_qdate.month(), ende_qdate.day()),
            )
        except DomainException as e:
            QMessageBox.warning(self, APP_TITLE, str(e))
            return
        except Exception as e:
            QMessageBox.warning(self, APP_TITLE, str(e))
            return

        self._refresh_table()
        self._clear_form()
        self._set_edit_fields_enabled(False)
