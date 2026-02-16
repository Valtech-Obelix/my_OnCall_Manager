import sys
from   PySide6.QtWidgets                              import QApplication
from   src.ui.main_window                             import MainWindow
from   src.infrastructure.database                    import Database
from   src.infrastructure.incident_analyst_repository import IncidentAnalystRepository
from   src.domain.incident_analyst                    import IncidentAnalyst


class Application:

    def __init__(self):
        self._qt_app = QApplication(sys.argv)

        self._database = Database()
        self._database.initialize_schema()

        self._repository = IncidentAnalystRepository(
            self._database.get_connection()
        )

        self._main_window = MainWindow()

    def add_incident_analyst(self, p_name: str, p_email: str) -> IncidentAnalyst:
        analyst = IncidentAnalyst(
            id=None,
            name=p_name,
            email=p_email
        )

        return self._repository.add(analyst)

    def run(self):
        self._main_window.show()
        return self._qt_app.exec()
