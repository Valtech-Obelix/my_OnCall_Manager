from     PySide6.QtWidgets                                 import (  QDialog
                                                                   , QLabel
                                                                   , QListWidget
                                                                   , QPushButton
                                                                   , QVBoxLayout
                                                                   , QHBoxLayout
                                                                   , QWidget
                                                                  )
from     PySide6.QtCore                                    import (Qt)

APP_TITLE = "Incident Analyst Verwaltung"
LABEL_CURRENT = "Aktuelle Incidentanalysten"


class IncidentAnalystDialog(QDialog):

    def __init__(self, p_application, p_parent=None):
        super().__init__(p_parent)

        self._application = p_application

        self._setup_ui()
        self._refresh_list()

    # Ref: UI-Strukturierung für IncidentAnalyst Modul
    def _setup_ui(self):

        self.setWindowTitle(APP_TITLE)
        self.resize(700, 400)

        main_layout = QVBoxLayout()

        # Titel
        title_label = QLabel(LABEL_CURRENT)
        main_layout.addWidget(title_label)

        # Horizontaler Bereich: Liste + Buttons
        content_layout = QHBoxLayout()

        # Liste
        self._analyst_list = QListWidget()
        content_layout.addWidget(self._analyst_list)

        # Button-Spalte
        button_layout = QVBoxLayout()

        self._add_button = QPushButton("+")
        self._delete_button = QPushButton("🗑")
        self._add_button.setFixedWidth(60)
        self._delete_button.setFixedWidth(60)   

        button_layout.addWidget(self._add_button)
        button_layout.addWidget(self._delete_button)
        button_layout.addStretch()

        content_layout.addLayout(button_layout)

        main_layout.addLayout(content_layout)

        self._delete_button.clicked.connect(self._handle_delete)

        self.setLayout(main_layout)

    # Ref: UC-002 – Liste laden
    def _refresh_list(self):

        self._analyst_list.clear()

        analysts = self._application.get_all_incident_analysts()

        for analyst in analysts:
            item_text = f"{analyst.buchungsname} ({analyst.email})"
            self._analyst_list.addItem(item_text)

            item = self._analyst_list.item(self._analyst_list.count() - 1)
            item.setData(Qt.UserRole, analyst.id)

    def _handle_delete(self):

        selected_item = self._analyst_list.currentItem()

        if not selected_item:
            return

        analyst_id = selected_item.data(Qt.UserRole)

        self._application.delete_incident_analyst(analyst_id)

        self._refresh_list()
        