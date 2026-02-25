from    PySide6.QtWidgets                                   import  (  QDialog
                                                                     , QVBoxLayout
                                                                     , QFormLayout
                                                                     , QLineEdit
                                                                     , QPushButton
                                                                     , QMessageBox
                                                                    )

from    src.domain.exceptions                               import  (  OpsGenieAuthException
                                                                     , OpsGenieNotFoundException
                                                                     , OpsGenieConnectionException
                                                                     , OpsGenieApiException
                                                                    )

SCHEDULE_ID                                                 =   '46d877bb-9df4-4a8c-b42c-322a1ee47623'

class OpsGenieImportDialog(QDialog):

    def __init__(self, p_opsgenie_service, p_parent=None):
        super().__init__(p_parent)

        self._service = p_opsgenie_service

        self.setWindowTitle('Import OpsGenie Shifts')
        self.setMinimumWidth(400)

        self._schedule_input = QLineEdit()
        self._schedule_input.setMinimumWidth(500)
        self._project_input = QLineEdit()
        self._project_input.setMinimumWidth(500)

        form_layout = QFormLayout()
        form_layout.addRow('Schedule ID:', self._schedule_input)
        form_layout.addRow('Project:', self._project_input)

        self._import_button = QPushButton('Import')
        self._import_button.clicked.connect(self._on_import_clicked)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(self._import_button)

        self.setLayout(layout)

    def _on_import_clicked(self):

        schedule_id = self._schedule_input.text().strip()
        project = self._project_input.text().strip()

        if not schedule_id or not project:
            QMessageBox.warning(
                self,
                'Input Missing',
                'Please provide Schedule ID and Project.'
            )
            return

        try:
            result = self._service.import_schedule(
                p_schedule_id=schedule_id,
                p_project=project
            )

            QMessageBox.information(
                self,
                'Import Finished',
                f'Imported: {result.imported}\n'
                f'Skipped: {result.skipped}\n'
                f'Errors: {result.errors}'
            )

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