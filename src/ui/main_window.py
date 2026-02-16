from   PySide6.QtWidgets               import (  QMainWindow
                                               , QLabel
                                               , QWidget
                                               , QVBoxLayout
                                              )


APP_TITLE                              = 'my_OnCall_Manager'
WELCOME_TEXT                           = 'Willkommen im my_OnCall_Manager'


class MainWindow(QMainWindow):

    def __init__(self, p_parent=None):
        super().__init__(p_parent)
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle(APP_TITLE)

        central_widget = QWidget()
        layout = QVBoxLayout()

        label = QLabel(WELCOME_TEXT)
        layout.addWidget(label)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
