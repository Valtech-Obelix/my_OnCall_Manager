from   PySide6.QtWidgets               import (  QMainWindow
                                               , QLabel
                                               , QWidget
                                               , QVBoxLayout
                                               , QLineEdit
                                               , QPushButton
                                               , QMessageBox
                                              )
from     datetime                      import date


APP_TITLE                              = 'my_OnCall_Manager'

# Ref: UC-001 v0.2 – UI angepasst
LABEL_VORNAMEN                      = 'Vornamen (getrennt durch Blanks)'
LABEL_NACHNAME                        = 'Nachname(n)'
LABEL_EMAIL                            = 'E-Mail'
LABEL_START                            = 'Startdatum (YYYY-MM-DD)'
LABEL_END                              = 'Enddatum (optional)'

BUTTON_SAVE                            = 'Speichern'
MESSAGE_SUCCESS                        = 'Incident Analyst gespeichert'


class MainWindow(QMainWindow):

    def __init__(self, p_application, p_parent=None):
        super().__init__(p_parent)
        self._application = p_application
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle(APP_TITLE)

        central_widget                 = QWidget()
        layout                         = QVBoxLayout()

         # Ref: UC-001 v0.2 – neue Eingabefelder
        self._vornamen_input        = QLineEdit()
        self._nachname_input          = QLineEdit()
        self._email_input              = QLineEdit()
        self._start_input              = QLineEdit()
        self._end_input                = QLineEdit()

        self._save_button              = QPushButton(BUTTON_SAVE)

        layout.addWidget(QLabel(LABEL_VORNAMEN))
        layout.addWidget(self._vornamen_input)

        layout.addWidget(QLabel(LABEL_NACHNAME))
        layout.addWidget(self._nachname_input)

        layout.addWidget(QLabel(LABEL_EMAIL))
        layout.addWidget(self._email_input)

        layout.addWidget(QLabel(LABEL_START))
        layout.addWidget(self._start_input)

        layout.addWidget(QLabel(LABEL_END))
        layout.addWidget(self._end_input)

        layout.addWidget(self._save_button)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self._save_button.clicked.connect(self._handle_save)

    def _handle_save(self):

        # Ref: UC-001 v0.2 – neue Felder
        vornamen                                   = self._vornamen_input.text()
        nachname                                     = self._nachname_input.text()
        email                                         = self._email_input.text()
        start                                         = self._start_input.text()
        end                                           = self._end_input.text()

        if not vornamen or not nachname or not email or not start:
            QMessageBox.warning(
                self,
                APP_TITLE,
                'Bitte alle Pflichtfelder ausfüllen'
            )
            return

        try:
            start_datum = date.fromisoformat(start)
            ende_datum  = date.fromisoformat(end) if end else None
        except ValueError:
            QMessageBox.warning(
                self,
                APP_TITLE,
                'Datum muss im Format YYYY-MM-DD sein'
            )
            return

        # Übergabe an Application-Schicht
        self._application.add_incident_analyst(
            vornamen,
            nachname,
            email,
            start_datum,
            ende_datum
        )

        QMessageBox.information(self, APP_TITLE, MESSAGE_SUCCESS)

        self._vornamen_input.clear()
        self._nachname_input.clear()
        self._email_input.clear()
        self._start_input.clear()
        self._end_input.clear()
