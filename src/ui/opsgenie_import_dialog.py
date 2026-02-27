from    PySide6.QtWidgets                                   import  (  QDialog
                                                                     , QVBoxLayout
                                                                     , QHBoxLayout
                                                                     , QFormLayout
                                                                     , QLineEdit
                                                                     , QComboBox
                                                                     , QPushButton
                                                                     , QMessageBox
                                                                    )

from    src.domain.exceptions                               import  (  OpsGenieAuthException
                                                                     , OpsGenieNotFoundException
                                                                     , OpsGenieConnectionException
                                                                     , OpsGenieApiException
                                                                    )

class OpsGenieImportDialog(QDialog):

    def __init__(self, p_opsgenie_service, p_parent=None):
        super().__init__(p_parent)

        self._service = p_opsgenie_service

        self.setWindowTitle('Import OpsGenie Shifts')
        self.setMinimumWidth(400)

        self._schedule_name_combo = QComboBox()
        self._schedule_name_combo.setMinimumWidth(500)
        self._schedule_name_combo.setEditable(True)
        self._schedule_name_combo.setInsertPolicy(QComboBox.NoInsert)
        self._schedule_name_combo.lineEdit().setPlaceholderText(
            'Namen des Schichtplans eingeben'
        )
        self._schedule_name_combo.currentIndexChanged.connect(
            self._on_schedule_name_selected
        )

        self._schedule_id_input = QLineEdit()
        self._schedule_id_input.setMinimumWidth(500)
        self._schedule_id_input.setPlaceholderText('Schedule ID eingeben')

        form_layout = QFormLayout()
        form_layout.addRow('Name des Schichtplans:', self._schedule_name_combo)
        form_layout.addRow('Schedule ID:', self._schedule_id_input)

        self._import_button = QPushButton('Schichten importieren')
        self._import_button.clicked.connect(self._on_import_clicked)
        self._close_button = QPushButton('Fertig')
        self._close_button.clicked.connect(self.reject)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self._import_button)
        button_layout.addWidget(self._close_button)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self._load_history()

    def _load_history(self):
        self._schedule_name_combo.clear()
        self._schedule_name_combo.addItem('')

        history = self._service.get_import_history()
        for entry in history:
            schedule_id = entry.get("schedule_id", "")
            schedule_name = (
                entry.get("schedule_name", "")
                or entry.get("project", "")
            )
            last_import = entry.get("last_import", "")

            if schedule_name:
                label = f'{schedule_name} - zuletzt: {last_import}'
            else:
                label = f'{schedule_id} - zuletzt: {last_import}'
            self._schedule_name_combo.addItem(label)
            self._schedule_name_combo.setItemData(
                self._schedule_name_combo.count() - 1,
                entry
            )

        if history:
            # Standardmäßig den zuletzt verwendeten Schichtplan vorbelegen.
            self._schedule_name_combo.setCurrentIndex(1)
            self._on_schedule_name_selected(1)
        else:
            self._schedule_name_combo.setCurrentIndex(0)
            self._schedule_id_input.clear()

    def _on_schedule_name_selected(self, p_index: int):
        if p_index <= 0:
            return

        entry = self._schedule_name_combo.itemData(p_index)
        if not entry:
            return

        schedule_name = (
            entry.get("schedule_name", "")
            or entry.get("project", "")
        )
        self._schedule_name_combo.setEditText(schedule_name)
        self._schedule_id_input.setText(entry.get("schedule_id", ""))

    def _on_import_clicked(self):

        schedule_name = self._schedule_name_combo.currentText().strip()
        schedule_id = self._schedule_id_input.text().strip()

        if not schedule_id or not schedule_name:
            QMessageBox.warning(
                self,
                'Input Missing',
                'Bitte Schedule ID und Name des Schichtplans angeben.'
            )
            return

        try:
            result = self._service.import_schedule(
                p_schedule_id=schedule_id,
                p_schedule_name=schedule_name
            )

            QMessageBox.information(
                self,
                'Import Finished',
                f'Imported: {result.imported}\n'
                f'Skipped: {result.skipped}\n'
                f'Errors: {result.errors}'
            )
            self._load_history()
            self._schedule_name_combo.setEditText(schedule_name)
            self._schedule_id_input.setText(schedule_id)

        except OpsGenieAuthException:
            QMessageBox.critical(
                self,
                'Authentication Error',
                'OpsGenie authentication failed.'
            )

        except OpsGenieNotFoundException:
            QMessageBox.critical(
                self,
                'Not Found',
                'Schedule not found.'
            )

        except OpsGenieConnectionException:
            QMessageBox.critical(
                self,
                'Connection Error',
                'Could not reach OpsGenie API.'
            )

        except OpsGenieApiException as ex:
            QMessageBox.critical(
                self,
                'API Error',
                str(ex)
            )

        except Exception as ex:
            QMessageBox.critical(
                self,
                'Unexpected Error',
                str(ex)
            )
