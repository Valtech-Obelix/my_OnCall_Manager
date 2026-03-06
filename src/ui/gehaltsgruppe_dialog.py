from datetime import date

from PySide6.QtCore import QEvent, Qt
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QComboBox,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.domain.exceptions import DomainException


APP_TITLE = "Gehaltsgruppen verwalten"


class GehaltsgruppeDialog(QDialog):
    def __init__(self, p_application, p_parent=None):
        super().__init__(p_parent)
        self._application = p_application
        self._selected_group_id: int | None = None
        self._is_edit_mode = False
        self._setup_ui()
        self._refresh_table()
        self._set_edit_fields_enabled(False)
        self._set_primary_action_button(self._new_button)

    def _setup_ui(self) -> None:
        self.setWindowTitle(APP_TITLE)
        self.resize(980, 620)

        main_layout = QVBoxLayout()
        grid = QGridLayout()
        grid.setColumnStretch(0, 2)
        grid.setColumnStretch(1, 1)
        grid.setRowStretch(0, 1)

        display_group = QGroupBox("Anzeige")
        display_layout = QVBoxLayout()

        self._group_table = QTableWidget()
        self._group_table.setColumnCount(3)
        self._group_table.setHorizontalHeaderLabels(["ID", "Bezeichnung", "Standort"])
        self._group_table.setSelectionBehavior(QTableWidget.SelectRows)
        self._group_table.setSelectionMode(QTableWidget.SingleSelection)
        self._group_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._group_table.itemSelectionChanged.connect(self._on_group_selected)
        display_layout.addWidget(self._group_table)

        self._history_table = QTableWidget()
        self._history_table.setColumnCount(2)
        self._history_table.setHorizontalHeaderLabels(["Gueltig ab", "Betrag"])
        self._history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._history_table.setSelectionMode(QTableWidget.NoSelection)
        display_layout.addWidget(self._history_table)

        display_group.setLayout(display_layout)
        grid.addWidget(display_group, 0, 0)

        edit_group = QGroupBox("Edit")
        edit_layout = QFormLayout()
        self._name_input = QLineEdit()
        self._amount_input = QLineEdit()
        self._effective_input = QLineEdit()
        self._effective_input.setPlaceholderText("tt.mm.jj")
        self._location_combo = QComboBox()
        self._name_input.installEventFilter(self)
        self._amount_input.installEventFilter(self)
        self._effective_input.installEventFilter(self)

        edit_layout.addRow("Bezeichnung:", self._name_input)
        edit_layout.addRow("Betrag:", self._amount_input)
        edit_layout.addRow("Gueltig ab:", self._effective_input)
        edit_layout.addRow("Standort:", self._location_combo)
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
        buttons1_layout.addWidget(self._new_button)
        buttons1_layout.addWidget(self._edit_button)
        buttons1_layout.addWidget(self._save_button)
        buttons1_layout.addStretch()
        buttons1_group.setLayout(buttons1_layout)
        grid.addWidget(buttons1_group, 1, 0)

        buttons2_group = QWidget()
        buttons2_layout = QHBoxLayout()
        buttons2_layout.setContentsMargins(0, 0, 0, 0)
        close_button = QPushButton("Dialog schließen")
        close_button.clicked.connect(self.close)
        buttons2_layout.addStretch()
        buttons2_layout.addWidget(close_button)
        buttons2_group.setLayout(buttons2_layout)
        grid.addWidget(buttons2_group, 1, 1)

        main_layout.addLayout(grid)
        self.setLayout(main_layout)
        self._load_oncall_locations()

    def _refresh_table(self) -> None:
        groups = self._application.get_gehaltsgruppen()
        self._group_table.blockSignals(True)
        self._group_table.setRowCount(len(groups))
        for row_index, group in enumerate(groups):
            group_id = int(group.id)
            id_item = QTableWidgetItem(str(group_id))
            id_item.setData(Qt.UserRole, group_id)
            self._group_table.setItem(row_index, 0, id_item)
            self._group_table.setItem(row_index, 1, QTableWidgetItem(str(group.bezeichnung)))
            self._group_table.setItem(row_index, 2, QTableWidgetItem(str(group.oncall_location_id)))

        self._group_table.resizeColumnsToContents()
        self._group_table.clearSelection()
        self._group_table.blockSignals(False)

        self._history_table.setRowCount(0)
        self._selected_group_id = None
        self._set_primary_action_button(self._new_button)

    def _on_group_selected(self) -> None:
        row = self._group_table.currentRow()
        if row < 0:
            return

        id_item = self._group_table.item(row, 0)
        name_item = self._group_table.item(row, 1)
        if id_item is None or name_item is None:
            return

        self._selected_group_id = int(id_item.data(Qt.UserRole))
        self._name_input.setText(name_item.text())
        location_text = str(self._group_table.item(row, 2).text() if self._group_table.item(row, 2) else "GER")
        location_idx = self._location_combo.findText(location_text)
        if location_idx < 0:
            self._location_combo.addItem(location_text)
            location_idx = self._location_combo.findText(location_text)
        self._location_combo.setCurrentIndex(location_idx)
        self._amount_input.clear()
        self._effective_input.clear()
        self._set_edit_fields_enabled(False)
        self._set_primary_action_button(self._edit_button)
        self._load_history(self._selected_group_id)

    def _load_oncall_locations(self) -> None:
        current = self._location_combo.currentText()
        self._location_combo.clear()
        for location in self._application.get_oncall_locations():
            self._location_combo.addItem(location["id"])

        if self._location_combo.count() == 0:
            self._location_combo.addItem("GER")

        preferred = current or "GER"
        idx = self._location_combo.findText(preferred)
        if idx < 0:
            idx = 0
        self._location_combo.setCurrentIndex(idx)

    def _load_history(self, p_group_id: int) -> None:
        rows = self._application.get_gehaltsgruppe_betraege(p_group_id)
        self._history_table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            self._history_table.setItem(
                row_index,
                0,
                QTableWidgetItem(self._format_date_for_display(str(row.get("gueltig_ab", "")))),
            )
            self._history_table.setItem(
                row_index,
                1,
                QTableWidgetItem(str(row.get("betrag", ""))),
            )
        self._history_table.resizeColumnsToContents()

    def _on_new_clicked(self) -> None:
        self._is_edit_mode = False
        self._selected_group_id = None
        self._group_table.clearSelection()
        self._name_input.clear()
        self._amount_input.clear()
        self._effective_input.clear()
        self._load_oncall_locations()
        ger_idx = self._location_combo.findText("GER")
        if ger_idx >= 0:
            self._location_combo.setCurrentIndex(ger_idx)
        self._set_edit_fields_enabled(True)
        self._name_input.setEnabled(True)
        self._location_combo.setEnabled(True)
        self._set_primary_action_button(self._save_button)
        self._name_input.setFocus()

    def _on_edit_clicked(self) -> None:
        if self._selected_group_id is None:
            QMessageBox.information(self, APP_TITLE, "Bitte zuerst einen Eintrag auswählen.")
            return

        self._is_edit_mode = True
        self._set_edit_fields_enabled(True)
        self._name_input.setEnabled(False)
        self._location_combo.setEnabled(True)
        self._amount_input.setFocus()
        self._set_primary_action_button(self._save_button)

    def _on_save_clicked(self) -> None:
        try:
            selected_location = self._location_combo.currentText().strip().upper()
            if self._is_edit_mode:
                if self._selected_group_id is None:
                    QMessageBox.information(self, APP_TITLE, "Bitte zuerst einen Eintrag auswählen.")
                    return

                changed = False
                current_row = self._group_table.currentRow()
                current_location_item = (
                    self._group_table.item(current_row, 2)
                    if current_row >= 0
                    else None
                )
                current_location = str(current_location_item.text()) if current_location_item else ""

                if selected_location != current_location:
                    self._application.update_gehaltsgruppe_oncall_location(
                        p_group_id=self._selected_group_id,
                        p_oncall_location_id=selected_location,
                    )
                    changed = True

                amount_text = self._amount_input.text().strip()
                effective_text = self._effective_input.text().strip()
                if amount_text or effective_text:
                    if not amount_text or not effective_text:
                        raise ValueError("Bei Betragänderung müssen Betrag und Gueltig-ab gesetzt sein.")
                    amount = self._parse_amount(amount_text)
                    effective_date = self._parse_date(effective_text)
                    self._application.update_gehaltsgruppe_betrag(
                        p_group_id=self._selected_group_id,
                        p_betrag=amount,
                        p_gueltig_ab=effective_date,
                    )
                    changed = True

                if not changed:
                    QMessageBox.information(self, APP_TITLE, "Keine Änderung zum Speichern vorhanden.")
                    return
            else:
                amount = self._parse_amount(self._amount_input.text())
                effective_date = self._parse_date(self._effective_input.text())
                self._application.create_gehaltsgruppe(
                    p_bezeichnung=self._name_input.text().strip(),
                    p_betrag=amount,
                    p_gueltig_ab=effective_date,
                    p_oncall_location_id=selected_location,
                )
        except (DomainException, ValueError) as exc:
            QMessageBox.warning(self, APP_TITLE, str(exc))
            return

        self._is_edit_mode = False
        self._set_edit_fields_enabled(False)
        self._name_input.clear()
        self._amount_input.clear()
        self._effective_input.clear()
        self._refresh_table()

    def _on_name_return_pressed(self) -> None:
        if not self._name_input.isEnabled():
            return
        self._amount_input.setFocus()
        self._amount_input.selectAll()

    def _on_amount_return_pressed(self) -> None:
        if not self._amount_input.isEnabled():
            return
        self._effective_input.setFocus()
        self._effective_input.selectAll()

    def _on_effective_return_pressed(self) -> None:
        if not self._effective_input.isEnabled():
            return
        self._set_primary_action_button(self._save_button)
        self._save_button.setFocus()

    def eventFilter(self, p_object, p_event):
        if p_event.type() == QEvent.KeyPress and p_event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if p_object is self._name_input and self._name_input.isEnabled():
                self._on_name_return_pressed()
                return True
            if p_object is self._amount_input and self._amount_input.isEnabled():
                self._on_amount_return_pressed()
                return True
            if p_object is self._effective_input and self._effective_input.isEnabled():
                self._on_effective_return_pressed()
                return True
        return super().eventFilter(p_object, p_event)

    def _set_edit_fields_enabled(self, p_enabled: bool) -> None:
        self._name_input.setEnabled(p_enabled)
        self._amount_input.setEnabled(p_enabled)
        self._effective_input.setEnabled(p_enabled)
        self._location_combo.setEnabled(p_enabled)

    def _set_primary_action_button(self, p_button: QPushButton) -> None:
        for button in (self._new_button, self._edit_button, self._save_button):
            button.setDefault(False)
            button.setAutoDefault(False)
        p_button.setAutoDefault(True)
        p_button.setDefault(True)

    def _parse_date(self, p_text: str) -> date:
        text = p_text.strip()
        if not text:
            raise DomainException("Gueltig-ab-Datum ist erforderlich.")
        try:
            day, month, year = text.split(".")
            return date(year=2000 + int(year), month=int(month), day=int(day))
        except ValueError as exc:
            raise ValueError("Datum muss im Format tt.mm.jj sein.") from exc

    def _format_date_for_display(self, p_iso_date: str) -> str:
        if not p_iso_date:
            return ""
        parsed = date.fromisoformat(p_iso_date)
        return parsed.strftime("%d.%m.%y")

    def _parse_amount(self, p_text: str) -> float:
        normalized = p_text.strip().replace(",", ".")
        if not normalized:
            raise DomainException("Betrag ist erforderlich.")
        try:
            value = float(normalized)
        except ValueError as exc:
            raise ValueError("Betrag muss numerisch sein.") from exc
        if value < 0:
            raise DomainException("Betrag darf nicht negativ sein.")
        return value
