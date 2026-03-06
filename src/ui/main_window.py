from    PySide6.QtCore                                      import QUrl
from    PySide6.QtGui                                       import QAction, QDesktopServices
from    PySide6.QtWidgets                                   import  (
                                                                        QMainWindow,
                                                                        QLabel,
                                                                        QMessageBox,
                                                                        QWidget,
                                                                        QVBoxLayout,
                                                                    )
from    pathlib                                             import Path
from    src.infrastructure.runtime_paths                    import resource_path
from    src.ui.incident_analyst_dialog                      import  IncidentAnalystDialog
from    src.ui.opsgenie_import_dialog                       import  OpsGenieImportDialog
from    src.ui.shift_plan_view_dialog                       import  ShiftPlanViewDialog
from    src.ui.incident_analyst_shift_count_dialog          import  IncidentAnalystShiftCountDialog
from    src.ui.oncall_location_dialog                       import  OnCallLocationDialog
from    src.ui.shift_booking_compare_dialog                 import  ShiftBookingCompareDialog
from    src.ui.location_shift_distribution_dialog           import  LocationShiftDistributionDialog
from    src.ui.monthly_compensation_dialog                 import  MonthlyCompensationDialog
from    src.ui.gehaltsgruppe_dialog                        import  GehaltsgruppeDialog
from    src.ui.client_utilized_cost_dialog                 import  ClientUtilizedCostDialog
from    src.ui.overtime_cost_dialog                        import  OvertimeCostDialog
from    src.ui.on_call_cost_dialog                         import  OnCallCostDialog
from    src.ui.budget_management_dialog                    import  BudgetManagementDialog


APP_TITLE                               =   'my_OnCall_Manager'
ACTION_MANAGE_ANALYSTS                  =   'der Mitarbeiter'
ACTION_IMPORT_SHIFTS                    =   'OpsGenie Schichten importieren'
ACTION_VIEW_SHIFT_PLAN                  =   'Schichtplan anzeigen'
ACTION_VIEW_IA_SHIFT_COUNTS             =   'Aktive IA Schichtanzahl anzeigen'
ACTION_VIEW_ONCALL_LOCATIONS            =   'der Rufbereitschaftsstandorte'
ACTION_MANAGE_GEHALTSGRUPPEN            =   'der Gehaltsgruppen'
ACTION_MANAGE_BUDGETS                   =   'des Budgets'
ACTION_COMPARE_SHIFTS_BOOKINGS          =   'Schichtplan vs. Buchungen vergleichen'
ACTION_LOCATION_SHIFT_DISTRIBUTION      =   'Schichtverteilung nach Standort'
ACTION_MONTHLY_COMPENSATION             =   'Monatsabrechnung IA-Auszahlung'
ACTION_TEST_CLIENT_UTILIZED_COSTS       =   'Client Utilized Kosten testen'
ACTION_TEST_OVERTIME_COSTS             =   'Overtime Kosten testen'
ACTION_TEST_ON_CALL_COSTS              =   'On Call Kosten testen'
ACTION_OPEN_BOOKING_FOLDER              =   'CSV-Ordner öffnen'
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
        background_path = resource_path("src", "resources", "evoli.png")
        if not background_path.exists():
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
        action_manage_gehaltsgruppen = QAction(ACTION_MANAGE_GEHALTSGRUPPEN, self)
        action_manage_gehaltsgruppen.triggered.connect(self._open_gehaltsgruppe_dialog)
        management_menu.addAction(action_manage_gehaltsgruppen)

        action_manage_budgets = QAction(ACTION_MANAGE_BUDGETS, self)
        action_manage_budgets.triggered.connect(self._open_budget_management_dialog)
        management_menu.addAction(action_manage_budgets)

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
            action_import_shifts.setToolTip('OpsGenie API-Key fehlt.')
        shift_menu.addAction(action_import_shifts)

        action_view_shift_plan = QAction(ACTION_VIEW_SHIFT_PLAN, self)
        action_view_shift_plan.triggered.connect(self._open_shift_plan_view_dialog)
        shift_menu.addAction(action_view_shift_plan)

        action_open_booking_folder = QAction(ACTION_OPEN_BOOKING_FOLDER, self)
        action_open_booking_folder.triggered.connect(self._open_booking_csv_folder)
        shift_menu.addAction(action_open_booking_folder)

        analysis_menu = menu_bar.addMenu("Auswertung")
        action_ia_shift_counts = QAction(ACTION_VIEW_IA_SHIFT_COUNTS, self)
        action_ia_shift_counts.triggered.connect(self._open_incident_analyst_shift_count_dialog)
        analysis_menu.addAction(action_ia_shift_counts)

        action_compare_shifts = QAction(ACTION_COMPARE_SHIFTS_BOOKINGS, self)
        action_compare_shifts.triggered.connect(self._open_shift_booking_compare_dialog)
        analysis_menu.addAction(action_compare_shifts)

        action_location_distribution = QAction(ACTION_LOCATION_SHIFT_DISTRIBUTION, self)
        action_location_distribution.triggered.connect(self._open_location_shift_distribution_dialog)
        analysis_menu.addAction(action_location_distribution)

        action_monthly_compensation = QAction(ACTION_MONTHLY_COMPENSATION, self)
        action_monthly_compensation.triggered.connect(self._open_monthly_compensation_dialog)
        analysis_menu.addAction(action_monthly_compensation)

        action_client_utilized_costs = QAction(ACTION_TEST_CLIENT_UTILIZED_COSTS, self)
        action_client_utilized_costs.triggered.connect(self._open_client_utilized_cost_dialog)
        analysis_menu.addAction(action_client_utilized_costs)

        action_overtime_costs = QAction(ACTION_TEST_OVERTIME_COSTS, self)
        action_overtime_costs.triggered.connect(self._open_overtime_cost_dialog)
        analysis_menu.addAction(action_overtime_costs)

        action_on_call_costs = QAction(ACTION_TEST_ON_CALL_COSTS, self)
        action_on_call_costs.triggered.connect(self._open_on_call_cost_dialog)
        analysis_menu.addAction(action_on_call_costs)


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

    def _open_gehaltsgruppe_dialog(self):
        dialog = GehaltsgruppeDialog(self._application, self)
        dialog.exec()

    def _open_budget_management_dialog(self):
        dialog = BudgetManagementDialog(self._application, self)
        dialog.exec()

    def _open_shift_booking_compare_dialog(self):
        dialog = ShiftBookingCompareDialog(self._application, self)
        dialog.exec()

    def _open_location_shift_distribution_dialog(self):
        dialog = LocationShiftDistributionDialog(self._application, self)
        dialog.exec()

    def _open_monthly_compensation_dialog(self):
        dialog = MonthlyCompensationDialog(self._application, self)
        dialog.exec()

    def _open_client_utilized_cost_dialog(self):
        dialog = ClientUtilizedCostDialog(self._application, self)
        dialog.exec()

    def _open_overtime_cost_dialog(self):
        dialog = OvertimeCostDialog(self._application, self)
        dialog.exec()

    def _open_on_call_cost_dialog(self):
        dialog = OnCallCostDialog(self._application, self)
        dialog.exec()

    def _open_booking_csv_folder(self):
        booking_folder = self._application.get_booking_data_dir()
        opened = QDesktopServices.openUrl(QUrl.fromLocalFile(str(booking_folder)))
        if not opened:
            QMessageBox.warning(
                self,
                APP_TITLE,
                f"CSV-Ordner konnte nicht geoeffnet werden:\n{booking_folder}",
            )
