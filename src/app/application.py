import  sys
import  os
import  logging
from    PySide6.QtWidgets                                   import  QApplication
from    datetime                                            import  date

from    src.ui.main_window                                  import  MainWindow
from    src.infrastructure.database                         import  Database
from    src.infrastructure.incident_analyst_repository      import  IncidentAnalystRepository
from    src.services.incident_analyst_service               import  IncidentAnalystService
from    src.infrastructure.logging_config                   import  setup_logging
from    src.domain.incident_analyst                         import  IncidentAnalyst
from    src.infrastructure.shift_repository                 import  ShiftRepository
from    src.services.opsgenie_service                       import  OpsGenieService
from    src.infrastructure.opsgenie_client                  import  OpsGenieClient

class Application:

    def __init__(self):
        setup_logging()
        self._logger = logging.getLogger(__name__)
        self._logger.info('')
        self._logger.info('=====================')
        self._logger.info(" Application started ")
        self._logger.info('=====================')
        self._logger.info('')

        api_key = os.getenv('OPS_GENIE_API_KEY')
        self._opsgenie_client = None
        self._opsgenie_service = None
        if api_key:
            self._logger.info('OpsGenie API KEY geladen')
            self._opsgenie_client = OpsGenieClient(p_api_key=api_key)
        else:
            self._logger.warning(
                'OPS_GENIE_API_KEY ist nicht gesetzt. OpsGenie-Import ist deaktiviert.'
            )

        self._qt_app = QApplication(sys.argv)

        self._database = Database()
        self._database.initialize_schema()

        self._analyst_repository = IncidentAnalystRepository(self._database.get_connection())
        self._incident_analyst_service = IncidentAnalystService(self._analyst_repository)

        # Ref: UC-004 – vollständige Verdrahtung
        self._shift_repository = ShiftRepository(self._database.get_connection())
        if self._opsgenie_client is not None:
            self._opsgenie_service = OpsGenieService    (  p_client=self._opsgenie_client
                                                         , p_shift_repository=self._shift_repository
                                                         , p_analyst_repository=self._analyst_repository
                                                         , p_logger=self._logger
                                                        )

        self._main_window = MainWindow(self)

    @property
    def opsgenie_service(self):
        return self._opsgenie_service


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
        
