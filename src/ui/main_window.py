from    PySide6.QtWidgets                                   import  (  QMainWindow
                                                                     , QLabel
                                                                     , QWidget
                                                                     , QVBoxLayout
                                                                     , QPushButton
                                                                    )
from    PySide6.QtCore                                      import  Qt
from    datetime                                            import  date
from    src.ui.incident_analyst_dialog                      import  IncidentAnalystDialog
from    src.ui.opsgenie_import_dialog                       import  OpsGenieImportDialog


APP_TITLE                               =   'my_OnCall_Manager'
BUTTON_MANAGE_ANALYSTS                  =   'Incident Analysten verwalten'
BUTTON_IMPORT_SHIFTS                    =   'OpsGenie Schichten importieren'


class MainWindow(QMainWindow):

    def __init__(self, p_application, p_parent=None):
        super().__init__(p_parent)
        self._application = p_application
        self._setup_ui()

    def _setup_ui(self):

        self.setWindowTitle(APP_TITLE)
        self.resize(400, 200)

        central_widget = QWidget()
        layout = QVBoxLayout()

        title_label = QLabel("Hauptmenü")
        layout.addWidget(title_label)

        self._manage_button = QPushButton(BUTTON_MANAGE_ANALYSTS)
        self._manage_button.clicked.connect(self._open_incident_analyst_dialog)
        layout.addWidget(self._manage_button)

        self._import_button = QPushButton(BUTTON_IMPORT_SHIFTS)
        self._import_button.clicked.connect(self._open_import_dialog)
        layout.addWidget(self._import_button)

        layout.addStretch()

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


    def _open_incident_analyst_dialog(self):

        dialog = IncidentAnalystDialog(self._application, self)
        dialog.exec()

    def _open_import_dialog(self):
        dialog = OpsGenieImportDialog   (  p_opsgenie_service=self._application.opsgenie_service
                                         , p_parent=self
                                        )
        dialog.exec()
        
