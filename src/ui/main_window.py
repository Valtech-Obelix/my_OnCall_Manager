from   PySide6.QtWidgets               import (  QMainWindow
                                               , QLabel
                                               , QWidget
                                               , QVBoxLayout
                                               , QLabel
                                               , QLineEdit
                                               , QPushButton
                                               , QMessageBox
                                              )


APP_TITLE                              = 'my_OnCall_Manager'
LABEL_NAME                             = 'Name'
LABEL_EMAIL                            = 'E-Mail'
BUTTON_SAVE                            = 'Speichern'
MESSAGE_SUCCESS                        = 'Incident Analyst gespeichert'


class MainWindow(QMainWindow):

    def __init__(self, p_parent=None):
        super().__init__(p_parent)
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle(APP_TITLE)

        central_widget = QWidget()
        layout = QVBoxLayout()

        self._name_input = QLineEdit()
        self._email_input = QLineEdit()
        self._save_button = QPushButton(BUTTON_SAVE)

        layout.addWidget(QLabel(LABEL_NAME))
        layout.addWidget(self._name_input)

        layout.addWidget(QLabel(LABEL_EMAIL))
        layout.addWidget(self._email_input)

        layout.addWidget(self._save_button)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
