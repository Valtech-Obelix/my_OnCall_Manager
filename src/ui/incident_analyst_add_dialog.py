from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QDateEdit
)

from PySide6.QtCore import QDate
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

        # Vorname
        layout.addWidget(QLabel("Vorname"))
        self._vorname_input = QLineEdit()
        layout.addWidget(self._vorname_input)

        # Nachname
        layout.addWidget(QLabel("Nachname"))
        self._nachname_input = QLineEdit()
        layout.addWidget(self._nachname_input)

        # Email
        layout.addWidget(QLabel("E-Mail"))
        self._email_input = QLineEdit()
        layout.addWidget(self._email_input)

        # Startdatum
        layout.addWidget(QLabel("Startdatum"))
        self._start_input = QDateEdit()
        self._start_input.setCalendarPopup(True)
        self._start_input.setDate(QDate.currentDate())
        layout.addWidget(self._start_input)

        # Enddatum
        layout.addWidget(QLabel("Enddatum (optional)"))
        self._end_input = QDateEdit()
        self._end_input.setCalendarPopup(True)
        self._end_input.setSpecialValueText("Kein Enddatum")
        self._end_input.setDate(QDate.currentDate())
        layout.addWidget(self._end_input)

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

        end_date = date(
            end_qdate.year(),
            end_qdate.month(),
            end_qdate.day()
        )

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