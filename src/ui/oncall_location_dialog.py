from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
    QVBoxLayout,
)


APP_TITLE = "Rufbereitschaftsstandorte"


class OnCallLocationDialog(QDialog):
    def __init__(self, p_application, p_parent=None):
        super().__init__(p_parent)
        self._application = p_application
        self._selected_original_id: str | None = None
        self._setup_ui()
        self._refresh_table()
        self._set_edit_fields_enabled(False)
        self._set_primary_action_button(self._new_button)

    def _setup_ui(self):
        self.setWindowTitle(APP_TITLE)
        self.resize(860, 520)

        main_layout = QVBoxLayout()
        grid = QGridLayout()
        grid.setColumnStretch(0, 2)
        grid.setColumnStretch(1, 1)
        grid.setRowStretch(0, 1)

        display_group = QGroupBox("Lönder")
        display_layout = QVBoxLayout()
        self._table = QTableWidget()
        self._table.setColumnCount(2)
        self._table.setHorizontalHeaderLabels(["ID", "Name"])
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setSelectionMode(QTableWidget.SingleSelection)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.itemSelectionChanged.connect(self._on_row_selected)
        display_layout.addWidget(self._table)
        display_group.setLayout(display_layout)
        grid.addWidget(display_group, 0, 0)

        edit_group = QGroupBox("Edit")
        edit_layout = QFormLayout()
        self._id_input = QLineEdit()
        self._id_input.setMaxLength(3)
        self._id_input.setPlaceholderText("z.B. MUC")
        self._name_input = QLineEdit()
        self._name_input.setMaxLength(30)
        self._name_input.setPlaceholderText("Standortname (max 30)")
        edit_layout.addRow("ID (3 Zeichen):", self._id_input)
        edit_layout.addRow("Name (max 30):", self._name_input)
        edit_group.setLayout(edit_layout)
        grid.addWidget(edit_group, 0, 1)

        buttons1_group = QWidget()
        buttons1_layout = QHBoxLayout()
        buttons1_layout.setContentsMargins(0, 0, 0, 0)
        self._new_button = QPushButton("Neu")
        self._new_button.clicked.connect(self._on_new_clicked)
        self._edit_button = QPushButton("Bearbeiten")
        self._edit_button.clicked.connect(self._on_edit_clicked)
        self._save_button = QPushButton("Speichern")
        self._save_button.clicked.connect(self._on_save_clicked)
        self._delete_button = QPushButton("Löschen")
        self._delete_button.clicked.connect(self._on_delete_clicked)
        buttons1_layout.addWidget(self._new_button)
        buttons1_layout.addWidget(self._edit_button)
        buttons1_layout.addWidget(self._save_button)
        buttons1_layout.addWidget(self._delete_button)
        buttons1_layout.addStretch()
        buttons1_group.setLayout(buttons1_layout)
        grid.addWidget(buttons1_group, 1, 0)

        buttons2_group = QWidget()
        buttons2_layout = QHBoxLayout()
        buttons2_layout.setContentsMargins(0, 0, 0, 0)
        self._close_button = QPushButton("Dialog schließen")
        self._close_button.clicked.connect(self.close)
        buttons2_layout.addStretch()
        buttons2_layout.addWidget(self._close_button)
        buttons2_group.setLayout(buttons2_layout)
        grid.addWidget(buttons2_group, 1, 1)

        main_layout.addLayout(grid)
        self.setLayout(main_layout)

    def _refresh_table(self):
        rows = self._application.get_oncall_locations()
        self._table.setRowCount(len(rows))
        for row_index, entry in enumerate(rows):
            self._table.setItem(row_index, 0, QTableWidgetItem(entry["id"]))
            self._table.setItem(row_index, 1, QTableWidgetItem(entry["name"]))
        self._table.resizeColumnsToContents()

    def _on_row_selected(self):
        row = self._table.currentRow()
        if row < 0:
            return
        row_id = self._table.item(row, 0)
        row_name = self._table.item(row, 1)
        if row_id is None or row_name is None:
            return
        self._selected_original_id = row_id.text()
        self._id_input.setText(row_id.text())
        self._name_input.setText(row_name.text())
        self._set_primary_action_button(self._edit_button)
        self._set_edit_fields_enabled(False)

    def _clear_form(self):
        self._selected_original_id = None
        self._id_input.clear()
        self._name_input.clear()
        self._table.clearSelection()
        self._set_primary_action_button(self._new_button)

    def _on_new_clicked(self):
        self._clear_form()
        self._set_edit_fields_enabled(True)
        self._id_input.setFocus()

    def _on_edit_clicked(self):
        if not self._selected_original_id:
            QMessageBox.information(self, APP_TITLE, "Bitte zuerst einen Eintrag auswählen.")
            return
        self._set_edit_fields_enabled(True)
        self._id_input.setFocus()
        self._set_primary_action_button(self._edit_button)

    def _on_save_clicked(self):
        location_id = self._id_input.text().strip().upper()
        location_name = self._name_input.text().strip()

        if len(location_id) != 3:
            QMessageBox.warning(self, APP_TITLE, "ID muss genau 3 Zeichen lang sein.")
            return
        if len(location_name) == 0 or len(location_name) > 30:
            QMessageBox.warning(self, APP_TITLE, "Name muss zwischen 1 und 30 Zeichen haben.")
            return

        if (
            self._selected_original_id
            and self._selected_original_id != location_id
            and self._application.oncall_location_exists(location_id)
        ):
            QMessageBox.warning(self, APP_TITLE, "Die neue ID existiert bereits.")
            return

        if self._selected_original_id is None and self._application.oncall_location_exists(location_id):
            QMessageBox.warning(self, APP_TITLE, "ID existiert bereits.")
            return

        self._application.save_oncall_location(
            p_original_id=self._selected_original_id,
            p_id=location_id,
            p_name=location_name
        )
        self._refresh_table()
        self._clear_form()
        self._set_edit_fields_enabled(False)

    def _on_delete_clicked(self):
        if not self._selected_original_id:
            QMessageBox.information(self, APP_TITLE, "Bitte zuerst einen Eintrag auswählen.")
            return

        reply = QMessageBox.question(
            self,
            APP_TITLE,
            "Ausgewählten Standort wirklich löschen?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        self._application.delete_oncall_location(self._selected_original_id)
        self._refresh_table()
        self._clear_form()
        self._set_edit_fields_enabled(False)

    def _set_edit_fields_enabled(self, p_enabled: bool):
        self._id_input.setEnabled(p_enabled)
        self._name_input.setEnabled(p_enabled)

    def _set_primary_action_button(self, p_button: QPushButton):
        for button in (self._new_button, self._edit_button, self._save_button):
            button.setDefault(False)
            button.setAutoDefault(False)
        p_button.setAutoDefault(True)
        p_button.setDefault(True)
