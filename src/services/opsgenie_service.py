import  json
from    src.domain.import_result                            import  ImportResult
from    src.domain.shift                                    import  Shift
from    src.domain.exceptions                               import  (  OpsGenieApiException
                                                                     , OpsGenieAuthException
                                                                     , OpsGenieConnectionException
                                                                     , OpsGenieNotFoundException
                                                                    )

class OpsGenieService:

    def __init__(
        self,
        p_client,
        p_shift_repository,
        p_analyst_repository,
        p_logger
    ):
        self._client = p_client
        self._shift_repository = p_shift_repository
        self._analyst_repository = p_analyst_repository
        self._logger = p_logger

    def import_schedule(
        self,
        p_schedule_id: str,
        p_schedule_name: str
    ) -> ImportResult:

        imported = 0
        skipped = 0
        errors = 0

        try:
            timeline = self._client.get_schedule_timeline(p_schedule_id)

            self._logger.debug('=== RAW OPSGENIE RESPONSE START ===')
            self._logger.debug(json.dumps(timeline, indent=2))
            self._logger.debug('=== RAW OPSGENIE RESPONSE END ===')

        except (
            OpsGenieAuthException,
            OpsGenieNotFoundException,
            OpsGenieConnectionException,
            OpsGenieApiException
        ) as ex:
            self._logger.error(f'OpsGenie API error: {ex}')
            raise

        rotations = (
            timeline.get('data', {})
                    .get('finalTimeline', {})
                    .get('rotations', [])
        )

        for rotation in rotations:
            periods = rotation.get('periods', [])

            for period in periods:

                try:
                    recipient = period.get('recipient')

                    if not recipient:
                        skipped += 1
                        continue

                    if recipient.get('type') != 'user':
                        skipped += 1
                        continue

                    email = recipient.get('name')

                    if not email:
                        skipped += 1
                        continue

                    analyst = self._analyst_repository.find_by_email(email)

                    if not analyst:
                        self._logger.warning(
                            f'No analyst found for email: {email}'
                        )
                        skipped += 1
                        continue

                    shift = Shift(
                        p_id=None,
                        p_analyst_id=analyst.id,
                        p_project=p_schedule_name,
                        p_schedule_id=p_schedule_id,
                        p_start_time=period.get('startDate'),
                        p_end_time=period.get('endDate')
                    )

                    saved = self._shift_repository.save(shift)

                    if saved:
                        imported += 1
                    else:
                        skipped += 1

                except Exception as ex:
                    self._logger.error(f'Shift processing failed: {ex}')
                    errors += 1

        self._shift_repository.save_import_history(
            p_schedule_id=p_schedule_id,
            p_schedule_name=p_schedule_name
        )

        return ImportResult(
            p_imported=imported,
            p_skipped=skipped,
            p_errors=errors
        )

    def get_import_history(self) -> list[dict[str, str]]:
        return self._shift_repository.get_import_history()
