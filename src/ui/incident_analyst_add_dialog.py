from PySide6.QtWidgets                                     import (  QDialog
                                                                   , QLabel
                                                                   , QLineEdit
                                                                   , QPushButton
                                                                   , QVBoxLayout
                                                                   , QHBoxLayout
                                                                   , QMessageBox
                                                                   , QFormLayout
                                                                   , QDateEdit
                                                                  )
from PySide6.QtCore                                        import (  QDate
                                                                   , Qt
                                                                  )
from datetime import date


APP_TITLE = "Incident Analyst erfassen"


class IncidentAnalystAddDialog(QDialog):

    def __init__(self, p_application, p_parent=None):
        super().__init__(p_parent)

        self._application = p_application
        self._setup_ui()

    def _setup_ui(self):

        self.setWindowTitle(APP_TITLE)
        self.resize(400, 300)

        layout = QVBoxLayout()

        layout = QVBoxLayout()

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self._vorname_input = QLineEdit()
        self._nachname_input = QLineEdit()
        self._email_input = QLineEdit()

        self._start_input = QDateEdit()
        self._start_input.setCalendarPopup(True)
        self._start_input.setDate(QDate.currentDate())

        form_layout.addRow("Vorname.  :", self._vorname_input)
        form_layout.addRow("Nachname  :", self._nachname_input)
        form_layout.addRow("E-Mail.   :", self._email_input)
        form_layout.addRow("Startdatum:", self._start_input)

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()

        self._save_button = QPushButton("Speichern")
        self._cancel_button = QPushButton("Abbrechen")

        button_layout.addWidget(self._save_button)
        button_layout.addWidget(self._cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        self._save_button.clicked.connect(self._handle_save)
        self._cancel_button.clicked.connect(self.reject)

    def _handle_save(self):

        vorname = self._vorname_input.text()
        nachname = self._nachname_input.text()
        email = self._email_input.text()

        start_qdate = self._start_input.date()
        end_qdate = self._end_input.date()

        start_date = date(
            start_qdate.year(),
            start_qdate.month(),
            start_qdate.day()
        )

        end_date = None

        try:
            self._application.add_incident_analyst(
                vorname,
                nachname,
                email,
                start_date,
                end_date
            )
        except Exception as e:
            QMessageBox.warning(self, APP_TITLE, str(e))
            return

        self.accept()