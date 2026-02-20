from   PySide6.QtWidgets               import (  QMainWindow
                                               , QLabel
                                               , QWidget
                                               , QVBoxLayout
                                               , QPushButton
                                              )
from     PySide6.QtCore                import Qt
from     datetime                      import date
from     src.ui.incident_analyst_dialog import IncidentAnalystDialog


APP_TITLE                              = 'my_OnCall_Manager'
BUTTON_MANAGE_ANALYSTS                 = "Incident Analysten verwalten"


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
        layout.addWidget(self._manage_button)

        layout.addStretch()

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self._manage_button.clicked.connect(self._open_incident_analyst_dialog)

    def _open_incident_analyst_dialog(self):

        dialog = IncidentAnalystDialog(self._application, self)
        dialog.exec()
