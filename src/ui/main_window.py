from   PySide6.QtWidgets               import (  QMainWindow
                                               , QLabel
                                               , QWidget
                                               , QVBoxLayout
                                               , QLineEdit
                                               , QPushButton
                                               , QMessageBox
                                               , QListWidget
                                              )
from     PySide6.QtCore                import Qt
from     datetime                      import date


APP_TITLE                              = 'my_OnCall_Manager'

# Ref: UC-001 v0.2 – UI angepasst
LABEL_VORNAMEN                         = 'Vornamen (getrennt durch Blanks)'
LABEL_NACHNAME                         = 'Nachname(n)'
LABEL_EMAIL                            = 'E-Mail'
LABEL_START                            = 'Startdatum (YYYY-MM-DD)'
LABEL_END                              = 'Enddatum (optional)'

BUTTON_SAVE                            = 'Speichern'
BUTTON_DELETE                          = 'Ausgewählte(n) Incident Analysten löschen'
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
        self._vornamen_input           = QLineEdit()
        self._nachname_input           = QLineEdit()
        self._email_input              = QLineEdit()
        self._start_input              = QLineEdit()
        self._end_input                = QLineEdit()

        self._save_button              = QPushButton(BUTTON_SAVE)
        self._delete_button            = QPushButton(BUTTON_DELETE)

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
        layout.addWidget(self._delete_button)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Ref: UC-002 v0.1 – Liste der Incident Analysts
        self._analyst_list = QListWidget()
        layout.addWidget(self._analyst_list)

        self._save_button.clicked.connect(self._handle_save)
        self._delete_button.clicked.connect(self._handle_delete)

        self._refresh_analyst_list()

    def _handle_save(self):

        # Ref: UC-001 v0.2 – neue Felder
        vornamen                                      = self._vornamen_input.text()
        nachname                                      = self._nachname_input.text()
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
            start_datum = self._parse_date(start)
            ende_datum  = self._parse_date(end) if end else None
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

        self._refresh_analyst_list()

    # Ref: UC-001 v0.2 – deutsche Datumsformate unterstützen
    def _parse_date(self, p_value: str) -> date:
        """
        Unterstützt:
        1.1.26
        01.01.2026
        1.01.26
        """

        parts = p_value.strip().split('.')

        if len(parts) != 3:
            raise ValueError('Ungültiges Datumsformat.')

        day, month, year = parts

        day = int(day)
        month = int(month)

        # 2-stellige Jahreszahl behandeln
        if len(year) == 2:
            year = int(year)
            year += 2000 if year < 50 else 1900
        else:
            year = int(year)

        return date(year, month, day)

    # Ref: UC-002 v0.1 – Liste aktualisieren
    def _refresh_analyst_list(self):

        self._analyst_list.clear()

        analysts = self._application.get_all_incident_analysts()

        for analyst in analysts:
            item_text = f"{analyst.buchungsname} ({analyst.email})"
            self._analyst_list.addItem(item_text)

            item = self._analyst_list.item(self._analyst_list.count() - 1)
            item.setData(Qt.UserRole, analyst.id)

    # Ref: UC-002 v0.1 – Löschen eines Incident Analysts
    def _handle_delete(self):

        selected_item = self._analyst_list.currentItem()

        if not selected_item:
            QMessageBox.warning(
                self,
                APP_TITLE,
                'Bitte zuerst einen Incident Analyst auswählen.'
            )
            return

        reply = QMessageBox.question(
            self,
            APP_TITLE,
            'Möchten Sie den ausgewählten Incident Analyst wirklich löschen?',
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        analyst_id = selected_item.data(Qt.UserRole)

        self._application.delete_incident_analyst(analyst_id)

        self._refresh_analyst_list()