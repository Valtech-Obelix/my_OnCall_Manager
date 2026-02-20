import sys
from   PySide6.QtWidgets                              import QApplication
from   src.ui.main_window                             import MainWindow
from   src.infrastructure.database                    import Database
from   src.infrastructure.incident_analyst_repository import IncidentAnalystRepository
from   src.domain.incident_analyst                    import IncidentAnalyst
from   datetime                                       import date


class Application:

    def __init__(self):
        self._qt_app = QApplication(sys.argv)

        self._database = Database()
        self._database.initialize_schema()

        self._repository = IncidentAnalystRepository(
            self._database.get_connection()
        )

        self._main_window = MainWindow(self)

    def add_incident_analyst(self, 
                             p_vornamen               : str, 
                             p_nachname               : str,
                             p_email                  : str,
                             p_start_datum            : date,
                             p_ende_datum             : date) -> IncidentAnalyst:
        analyst = IncidentAnalyst(p_id=None, p_vornamen=p_vornamen, p_nachname=p_nachname, p_email=p_email, p_start_datum=p_start_datum, p_ende_datum=p_ende_datum)

        return self._repository.add(analyst)

    def run(self):
        self._main_window.show()
        return self._qt_app.exec()

    # Ref: UC-002 v0.1 – Laden aller Incident Analysts
    def get_all_incident_analysts(self):
        return self._repository.get_all()

    # Ref: UC-002 v0.1 – Löschen eines Incident Analysts
    def delete_incident_analyst(self, p_id: int):
        self._repository.delete(p_id)
        