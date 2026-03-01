from    PySide6.QtGui                                       import QAction
from    PySide6.QtWidgets                                   import  (
                                                                        QMainWindow,
                                                                        QLabel,
                                                                        QWidget,
                                                                        QVBoxLayout,
                                                                    )
from    pathlib                                             import Path
from    src.ui.incident_analyst_dialog                      import  IncidentAnalystDialog
from    src.ui.opsgenie_import_dialog                       import  OpsGenieImportDialog
from    src.ui.shift_plan_view_dialog                       import  ShiftPlanViewDialog
from    src.ui.incident_analyst_shift_count_dialog          import  IncidentAnalystShiftCountDialog
from    src.ui.oncall_location_dialog                       import  OnCallLocationDialog


APP_TITLE                               =   'my_OnCall_Manager'
ACTION_MANAGE_ANALYSTS                  =   'Incident Analysten verwalten'
ACTION_IMPORT_SHIFTS                    =   'OpsGenie Schichten importieren'
ACTION_VIEW_SHIFT_PLAN                  =   'Schichtplan anzeigen'
ACTION_VIEW_IA_SHIFT_COUNTS             =   'Aktive IA Schichtanzahl anzeigen'
ACTION_VIEW_ONCALL_LOCATIONS            =   'Rufbereitschaftsstandorte'
ACTION_CLOSE                            =   'Schließen'


class MainWindow(QMainWindow):

    def __init__(self, p_application, p_parent=None):
        super().__init__(p_parent)
        self._application = p_application
        self._setup_ui()

    def _setup_ui(self):

        self.setWindowTitle(APP_TITLE)
        self.resize(820, 520)

        central_widget = QWidget()
        central_widget.setObjectName("mainCentralWidget")
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title_card = QWidget()
        title_card.setObjectName("heroCard")
        title_card_layout = QVBoxLayout()
        title_card_layout.setContentsMargins(16, 12, 16, 12)
        title_card_layout.setSpacing(4)

        title_label = QLabel("my_OnCall_Manager")
        title_label.setObjectName("mainTitle")
        subtitle_label = QLabel("Navigation über die Menüleiste")
        subtitle_label.setObjectName("mainSubtitle")

        title_card_layout.addWidget(title_label)
        title_card_layout.addWidget(subtitle_label)
        title_card.setLayout(title_card_layout)
        layout.addWidget(title_card)
        layout.addStretch()

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        background_path = (Path(__file__).parent.parent / "resources" / "evoli.png").resolve()
        self.setStyleSheet(
            f"""
            #mainCentralWidget {{
                background-image: url("{background_path.as_posix()}");
                background-position: center;
                background-repeat: no-repeat;
                background-color: #10131a;
            }}
            #heroCard {{
                background-color: rgba(16, 19, 26, 170);
                border: 1px solid rgba(255, 255, 255, 90);
                border-radius: 10px;
            }}
            #mainTitle {{
                color: #ffffff;
                font-size: 24px;
                font-weight: 700;
            }}
            #mainSubtitle {{
                color: rgba(255, 255, 255, 220);
                font-size: 14px;
            }}
            """
        )
        self._setup_menu()

    def _setup_menu(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("Datei")
        action_close = QAction(ACTION_CLOSE, self)
        action_close.triggered.connect(self.close)
        file_menu.addAction(action_close)

        management_menu = menu_bar.addMenu("Verwaltung")
        action_manage_analysts = QAction(ACTION_MANAGE_ANALYSTS, self)
        action_manage_analysts.triggered.connect(self._open_incident_analyst_dialog)
        management_menu.addAction(action_manage_analysts)

        action_oncall_locations = QAction(ACTION_VIEW_ONCALL_LOCATIONS, self)
        action_oncall_locations.triggered.connect(self._open_oncall_location_dialog)
        management_menu.addAction(action_oncall_locations)

        shift_menu = menu_bar.addMenu("Schichtplan")
        action_import_shifts = QAction(ACTION_IMPORT_SHIFTS, self)
        action_import_shifts.triggered.connect(self._open_import_dialog)
        if self._application.opsgenie_service is None:
            action_import_shifts.setEnabled(False)
            action_import_shifts.setToolTip('OPS_GENIE_API_KEY fehlt.')
        shift_menu.addAction(action_import_shifts)

        action_view_shift_plan = QAction(ACTION_VIEW_SHIFT_PLAN, self)
        action_view_shift_plan.triggered.connect(self._open_shift_plan_view_dialog)
        shift_menu.addAction(action_view_shift_plan)

        analysis_menu = menu_bar.addMenu("Auswertung")
        action_ia_shift_counts = QAction(ACTION_VIEW_IA_SHIFT_COUNTS, self)
        action_ia_shift_counts.triggered.connect(self._open_incident_analyst_shift_count_dialog)
        analysis_menu.addAction(action_ia_shift_counts)


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

    def _open_oncall_location_dialog(self):
        dialog = OnCallLocationDialog(self._application, self)
        dialog.exec()
