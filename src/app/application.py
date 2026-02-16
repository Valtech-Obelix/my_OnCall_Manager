import sys
from   PySide6.QtWidgets               import QApplication
from   src.ui.main_window              import MainWindow
from   src.infrastructure.database     import Database


class Application:

    def __init__(self):
        self._qt_app = QApplication(sys.argv)
        self._main_window = MainWindow()
        self._database = Database()
        self._database.initialize_schema()

    def run(self):
        self._main_window.show()
        return self._qt_app.exec()
