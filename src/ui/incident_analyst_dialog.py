from     PySide6.QtWidgets                                 import (  QDialog
                                                                   , QLabel
                                                                   , QListWidget
                                                                   , QPushButton
                                                                   , QVBoxLayout
                                                                   , QHBoxLayout
                                                                   , QWidget
                                                                   , QMessageBox
                                                                   , QComboBox
                                                                  )
from     PySide6.QtCore                                    import (Qt)
from     src.ui.incident_analyst_add_dialog                import IncidentAnalystAddDialog
from     src.domain.exceptions                             import DomainException

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

        # Ref: UC-003_IA_deaktivieren
        # Combox für Auswahl des Filters
        self._filter_combo = QComboBox()
        self._filter_combo.addItems(["Alle", "Aktiv", "Inaktiv"])
        main_layout.addWidget(self._filter_combo)

        self._filter_combo.currentIndexChanged.connect(self._refresh_list)

        # Liste
        self._analyst_list = QListWidget()
        self._analyst_list.itemSelectionChanged.connect(self._update_button_state)
        content_layout.addWidget(self._analyst_list)

        # Button-Spalte
        button_layout = QVBoxLayout()
        self._add_button = QPushButton("+")
        self._add_button.setFixedWidth(60)
        button_layout.addWidget(self._add_button)

        # Ref: UC-002_IA_Löschen
        self._delete_button = QPushButton("🗑")
        self._delete_button.setFixedWidth(60)   
        self._delete_button.setEnabled(False)
        button_layout.addWidget(self._delete_button)

        # Ref: UC-003_IA_deaktiveren
        self._deactivate_button = QPushButton("Deaktivieren")
        button_layout.addWidget(self._deactivate_button)
        self._deactivate_button.setEnabled(False)
        self._deactivate_button.clicked.connect(self._handle_deactivate)

        button_layout.addStretch()
        content_layout.addLayout(button_layout)

        main_layout.addLayout(content_layout)

        self._add_button.clicked.connect(self._handle_add)
        self._delete_button.clicked.connect(self._handle_delete)

        self.setLayout(main_layout)

    # Ref: UC-002 – Liste laden
    def _refresh_list(self):

        self._analyst_list.clear()

        analysts = self._application.get_all_incident_analysts()

        filter_value = self._filter_combo.currentText()

        for analyst in analysts:

            if filter_value == "Aktiv" and not analyst.is_active:
                continue

            if filter_value == "Inaktiv" and analyst.is_active:
                continue

            item_text = analyst.buchungsname
            item = QListWidgetItem(item_text)

            if not analyst.is_active:
                item.setForeground(Qt.gray)

            item.setData(Qt.UserRole, analyst.id)
            self._analyst_list.addItem(item)
       
        self._analyst_list.setCurrentRow(-1)

    def _update_button_state(self):
        selected = self._analyst_list.currentItem() is not None
        self._delete_button.setEnabled(selected)

        # Ref: UC-003_IA_deaktiveren
        self._deactivate_button.setEnabled(selected)

    def _handle_add(self):

        dialog = IncidentAnalystAddDialog(self._application, self)

        if dialog.exec():
            self._refresh_list()

    def _handle_delete(self):

        selected_item = self._analyst_list.currentItem()

        if not selected_item:
            return
        
        reply = QMessageBox.question(
            self,
            APP_TITLE,
            "Ausgewählten Incident Analyst wirklich löschen?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        analyst_id = selected_item.data(Qt.UserRole)

        self._application.delete_incident_analyst(analyst_id)

        self._refresh_list()

    # Ref: UC-003_IA_deaktivieren
    def _handle_deactivate(self):

        selected_item = self._analyst_list.currentItem()

        if not selected_item:
            return

        analyst_id = selected_item.data(Qt.UserRole)

        dialog = QDialog(self)
        dialog.setWindowTitle("Enddatum festlegen")

        layout = QVBoxLayout()

        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate.currentDate())

        layout.addWidget(date_edit)

        button = QPushButton("Speichern")
        layout.addWidget(button)

        dialog.setLayout(layout)

        def save():
            qdate = date_edit.date()
            ende = date(qdate.year(), qdate.month(), qdate.day())
            try:
                self._application.deactivate_incident_analyst(analyst_id, ende)
                dialog.accept()
                self._refresh_list()
            except DomainException as e:
                QMessageBox.warning(self, APP_TITLE, str(e))

        button.clicked.connect(save)

        dialog.exec()
        
    