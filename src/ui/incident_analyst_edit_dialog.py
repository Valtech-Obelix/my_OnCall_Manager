from     datetime                                              import date

from     PySide6.QtCore                                        import QDate, Qt
from     PySide6.QtWidgets                                     import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from     src.domain.exceptions                                 import DomainException


APP_TITLE = "Incident Analyst bearbeiten"


class IncidentAnalystEditDialog(QDialog):

    def __init__(self, p_application, p_analyst, p_parent=None):
        super().__init__(p_parent)
        self._application = p_application
        self._analyst = p_analyst
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        self.setWindowTitle(APP_TITLE)
        self.resize(460, 330)

        layout = QVBoxLayout()

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self._vorname_input = QLineEdit()
        self._nachname_input = QLineEdit()
        self._email_input = QLineEdit()
        self._opsgenie_id_input = QLineEdit()
        self._oncall_location_input = QComboBox()
        self._oncall_location_input.setEditable(False)
        self._load_oncall_locations()

        self._start_input = QDateEdit()
        self._start_input.setCalendarPopup(True)

        self._end_enabled_checkbox = QCheckBox("Enddatum gesetzt")
        self._end_enabled_checkbox.toggled.connect(self._toggle_end_date_enabled)
        self._end_input = QDateEdit()
        self._end_input.setCalendarPopup(True)
        self._end_input.setEnabled(False)

        form_layout.addRow("Vorname.  :", self._vorname_input)
        form_layout.addRow("Nachname  :", self._nachname_input)
        form_layout.addRow("E-Mail.   :", self._email_input)
        form_layout.addRow("OpsGenie ID:", self._opsgenie_id_input)
        form_layout.addRow("Standort  :", self._oncall_location_input)
        form_layout.addRow("Startdatum:", self._start_input)
        form_layout.addRow("", self._end_enabled_checkbox)
        form_layout.addRow("Enddatum  :", self._end_input)

        layout.addWidget(QLabel("Daten des Incident Analysten bearbeiten"))
        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        self._save_button = QPushButton("Speichern")
        self._cancel_button = QPushButton("Abbrechen")
        button_layout.addWidget(self._save_button)
        button_layout.addWidget(self._cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self._save_button.clicked.connect(self._handle_save)
        self._cancel_button.clicked.connect(self.reject)

    def _load_data(self):
        self._vorname_input.setText(self._analyst.vornamen)
        self._nachname_input.setText(self._analyst.nachname)
        self._email_input.setText(self._analyst.email)
        self._opsgenie_id_input.setText(self._analyst.opsgenie_id or "")
        location_index = self._oncall_location_input.findText(self._analyst.oncall_location_id)
        if location_index < 0:
            self._oncall_location_input.addItem(self._analyst.oncall_location_id)
            location_index = self._oncall_location_input.findText(self._analyst.oncall_location_id)
        self._oncall_location_input.setCurrentIndex(location_index)

        self._start_input.setDate(
            QDate(
                self._analyst.start_datum.year,
                self._analyst.start_datum.month,
                self._analyst.start_datum.day,
            )
        )

        if self._analyst.ende_datum:
            self._end_enabled_checkbox.setChecked(True)
            self._end_input.setDate(
                QDate(
                    self._analyst.ende_datum.year,
                    self._analyst.ende_datum.month,
                    self._analyst.ende_datum.day,
                )
            )
        else:
            self._end_enabled_checkbox.setChecked(False)
            self._end_input.setDate(QDate.currentDate())

    def _toggle_end_date_enabled(self, p_checked: bool):
        self._end_input.setEnabled(p_checked)

    def _load_oncall_locations(self) -> None:
        locations = self._application.get_oncall_locations()
        if not locations:
            self._oncall_location_input.addItem("GER")
            return
        for location in locations:
            self._oncall_location_input.addItem(location["id"])

    def _handle_save(self):
        start_qdate = self._start_input.date()
        start_date = date(start_qdate.year(), start_qdate.month(), start_qdate.day())

        end_date = None
        if self._end_enabled_checkbox.isChecked():
            end_qdate = self._end_input.date()
            end_date = date(end_qdate.year(), end_qdate.month(), end_qdate.day())

        opsgenie_id = self._opsgenie_id_input.text().strip() or None

        try:
            self._application.update_incident_analyst(
                p_id=self._analyst.id,
                p_vornamen=self._vorname_input.text(),
                p_nachname=self._nachname_input.text(),
                p_email=self._email_input.text(),
                p_start_datum=start_date,
                p_ende_datum=end_date,
                p_opsgenie_id=opsgenie_id,
                p_oncall_location_id=self._oncall_location_input.currentText(),
            )
        except DomainException as e:
            QMessageBox.warning(self, APP_TITLE, str(e))
            return
        except Exception as e:
            QMessageBox.warning(self, APP_TITLE, str(e))
            return

        self.accept()
