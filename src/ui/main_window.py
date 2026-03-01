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
from    src.ui.shift_plan_view_dialog                       import  ShiftPlanViewDialog
from    src.ui.incident_analyst_shift_count_dialog          import  IncidentAnalystShiftCountDialog


APP_TITLE                               =   'my_OnCall_Manager'
BUTTON_MANAGE_ANALYSTS                  =   'Incident Analysten verwalten'
BUTTON_IMPORT_SHIFTS                    =   'OpsGenie Schichten importieren'
BUTTON_VIEW_SHIFT_PLAN                  =   'Schichtplan anzeigen'
BUTTON_VIEW_IA_SHIFT_COUNTS             =   'Aktive IA Schichtanzahl anzeigen'


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
        if self._application.opsgenie_service is None:
            self._import_button.setEnabled(False)
            self._import_button.setToolTip('OPS_GENIE_API_KEY fehlt.')
        layout.addWidget(self._import_button)

        self._view_shift_plan_button = QPushButton(BUTTON_VIEW_SHIFT_PLAN)
        self._view_shift_plan_button.clicked.connect(self._open_shift_plan_view_dialog)
        layout.addWidget(self._view_shift_plan_button)

        self._view_ia_shift_counts_button = QPushButton(BUTTON_VIEW_IA_SHIFT_COUNTS)
        self._view_ia_shift_counts_button.clicked.connect(
            self._open_incident_analyst_shift_count_dialog
        )
        layout.addWidget(self._view_ia_shift_counts_button)

        layout.addStretch()

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


    def _open_incident_analyst_dialog(self):

        dialog = IncidentAnalystDialog(self._application, self)
        dialog.exec()

    def _open_import_dialog(self):
        if self._application.opsgenie_service is None:
            return
        dialog = OpsGenieImportDialog   (  p_opsgenie_service=self._application.opsgenie_service
                                         , p_parent=self
                                        )
        dialog.exec()

    def _open_shift_plan_view_dialog(self):
        dialog = ShiftPlanViewDialog(self._application, self)
        dialog.exec()

    def _open_incident_analyst_shift_count_dialog(self):
        dialog = IncidentAnalystShiftCountDialog(self._application, self)
        dialog.exec()
