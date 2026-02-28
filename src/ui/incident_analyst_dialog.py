from     PySide6.QtWidgets                                 import (  QDialog
                                                                   , QLabel
                                                                   , QListWidget
                                                                   , QPushButton
                                                                   , QVBoxLayout
                                                                   , QHBoxLayout
                                                                   , QWidget
                                                                   , QMessageBox
                                                                   , QComboBox
                                                                   , QListWidgetItem
                                                                   , QDateEdit
                                                                   , QStyle
                                                                  )
from     PySide6.QtCore                                    import (  Qt
                                                                   , QDate
                                                                   , QSize
                                                                  )
from     PySide6.QtGui                                     import QIcon
from     src.ui.incident_analyst_add_dialog                import IncidentAnalystAddDialog
from     src.ui.incident_analyst_edit_dialog               import IncidentAnalystEditDialog
from     src.domain.exceptions                             import DomainException
from     datetime                                          import date
from     typing                                            import Callable
from     pathlib                                           import Path

APP_TITLE                                                  =      'Verwaltung der Incident Analysten'
LABEL_CURRENT                                              =      'Aktuelle Incidentanalysten'
ICON_PATH                                                  =      Path(__file__).parent.parent / 'resources' / 'icons'

class IncidentAnalystDialog(QDialog):

    def __init__(self, p_application, p_parent=None):
        super().__init__(p_parent)

        self._application = p_application

        self._setup_ui()
        self._refresh_list()

    def _create_icon_button(  self
                            , p_icon                       : QIcon
                            , p_width                      : int
                            , p_status                     : bool
                            , p_tool_tip                   : str
                            , p_callback                   : Callable | None = None
                            ) -> QPushButton:
        button = QPushButton()
        button.setFixedSize(p_width, 40)
        button.setIconSize(QSize(28, 28))
        button.setIcon(p_icon)
        button.setEnabled(p_status)
        button.setToolTip(p_tool_tip)
        if p_callback:
            button.clicked.connect(p_callback)
        button.setCursor(Qt.PointingHandCursor)

        return button

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
        self._add_button = self._create_icon_button(
              QIcon(str(ICON_PATH / 'user-plus.svg'))
            , 60
            , True
            , 'Neuen Incident Analysten anlegen'
            , self._handle_add
            )
        button_layout.addWidget(self._add_button)

        # Ref: UC-007_IA_Bearbeiten
        self._edit_button = self._create_icon_button(
              self.style().standardIcon(QStyle.SP_FileDialogDetailedView)
            , 60
            , False
            , 'ausgewählten Incident Analyst bearbeiten'
            , self._handle_edit
            )
        button_layout.addWidget(self._edit_button)

        # Ref: UC-002_IA_Löschen
        self._delete_button = self._create_icon_button(
              QIcon(str(ICON_PATH / 'user-minus.svg'))
            , 60
            , False
            , 'ausgewählten Incident Analyst löschen'
            , self._handle_delete
            )
        button_layout.addWidget(self._delete_button)

        # Ref: UC-003_IA_deaktiveren
        self._deactivate_button = self._create_icon_button(
              QIcon(str(ICON_PATH / 'user-pause.svg'))
            , 60
            , False
            , 'ausgewählten Incident Analysten deaktivieren'
            , self._handle_deactivate
            )
        button_layout.addWidget(self._deactivate_button)
    
        button_layout.addStretch()
        content_layout.addLayout(button_layout)

        main_layout.addLayout(content_layout)

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

            item.setData(Qt.UserRole, analyst)
            self._analyst_list.addItem(item)
       
        self._analyst_list.setCurrentRow(-1)

    def _update_button_state(self):
        selected = self._analyst_list.currentItem() is not None
        self._edit_button.setEnabled(selected)
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

        analyst = selected_item.data(Qt.UserRole)
        analyst_id = analyst.id

        self._application.delete_incident_analyst(analyst_id)

        self._refresh_list()

    def _handle_edit(self):

        selected_item = self._analyst_list.currentItem()

        if not selected_item:
            return

        analyst = selected_item.data(Qt.UserRole)

        dialog = IncidentAnalystEditDialog(self._application, analyst, self)
        if dialog.exec():
            self._refresh_list()

    # Ref: UC-003_IA_deaktivieren
    def _handle_deactivate(self):

        def save():
            qdate = date_edit.date()
            ende = date(qdate.year(), qdate.month(), qdate.day())
            try:
                self._application.deactivate_incident_analyst(analyst_id, ende)
                dialog.accept()
                self._refresh_list()
            except DomainException as e:
                QMessageBox.warning(self, APP_TITLE, str(e))

        selected_item = self._analyst_list.currentItem()

        if not selected_item:
            return

        analyst = selected_item.data(Qt.UserRole)
        analyst_id = analyst.id

        dialog = QDialog(self)
        dialog.setWindowTitle("Incident Analyst deaktivieren")

        layout = QVBoxLayout()

        label = QLabel("Inaktiv ab dem:")
        layout.addWidget(label)

        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate.currentDate())
        layout.addWidget(date_edit)

        button_layout = QHBoxLayout()

        save_button = QPushButton("Speichern")
        cancel_button = QPushButton("Abbrechen")

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        dialog.setLayout(layout)

        cancel_button.clicked.connect(dialog.reject)
        save_button.clicked.connect(save)

        dialog.exec()
        
    
