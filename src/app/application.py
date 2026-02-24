import   sys
import   logging
from     PySide6.QtWidgets                                 import QApplication
from     datetime                                          import date

from     src.ui.main_window                                import MainWindow
from     src.infrastructure.database                       import Database
from     src.infrastructure.incident_analyst_repository    import IncidentAnalystRepository
from     src.services.incident_analyst_service             import IncidentAnalystService
from     src.infrastructure.logging_config                 import setup_logging
from     src.domain.incident_analyst                       import IncidentAnalyst
from     src.infrastructure.shift_repository               import ShiftRepository
from     src.services.opsgenie_service                     import OpsGenieService

class Application:

    def __init__(self):
        setup_logging()
        self._logger = logging.getLogger(__name__)
        self._logger.info('')
        self._logger.info('=====================')
        self._logger.info(" Application started ")
        self._logger.info('=====================')
        self._logger.info('')

        self._qt_app = QApplication(sys.argv)

        self._database = Database()
        self._database.initialize_schema()

        repository = IncidentAnalystRepository(self._database.get_connection())
        self._incident_analyst_service = IncidentAnalystService(repository)

        # Ref: UC-004 – Shift Repository + OpsGenie Service
        self._shift_repository = ShiftRepository(self._database.get_connection())
        self._opsgenie_service = OpsGenieService(self._shift_repository)

        self._main_window = MainWindow(self)

    def add_incident_analyst(
        self,
        p_vornamen: str,
        p_nachname: str,
        p_email: str,
        p_start_datum: date,
        p_ende_datum: date | None = None
    ) -> IncidentAnalyst:

        return self._incident_analyst_service.create(
            p_vornamen,
            p_nachname,
            p_email,
            p_start_datum,
            p_ende_datum
        )

    def run(self):
        self._main_window.show()
        return self._qt_app.exec()

    # Ref: UC-002 v0.1 – Laden aller Incident Analysts
    def get_all_incident_analysts(self):
        return self._incident_analyst_service.get_all()

    # Ref: UC-002 v0.1 – Löschen eines Incident Analysts
    def delete_incident_analyst(self, p_id: int):
        self._incident_analyst_service.delete(p_id)

    # Ref: C-003: v.01 - Deaktiveren eines Incident Analysten
    def deactivate_incident_analyst(self, p_id: int, p_ende_datum):
        self._incident_analyst_service.deactivate(p_id, p_ende_datum)
        
    # Ref: UC-004 – Import OpsGenie Schedule
    def import_opsgenie_schedule(self, p_schedule_id: str) -> int:
        return self._opsgenie_service.import_schedule(p_schedule_id)
