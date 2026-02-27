import  json
from    datetime                                            import datetime
from    src.domain.import_result                            import  ImportResult
from    src.domain.shift                                    import  Shift
from    src.infrastructure.timezone_utils                   import  format_utc_as_berlin
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

        since, until, date_anchor, interval, interval_unit = self._get_import_window(
            p_schedule_id
        )

        try:
            timeline = self._client.get_schedule_timeline(
                p_schedule_id=p_schedule_id,
                p_since=since,
                p_until=until,
                p_date=date_anchor,
                p_interval=interval,
                p_interval_unit=interval_unit
            )

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

    def get_schedule_time_bounds_local(
        self,
        p_schedule_id: str
    ) -> tuple[str | None, str | None]:
        min_start, max_end = self._shift_repository.get_schedule_time_bounds(
            p_schedule_id
        )
        if not min_start or not max_end:
            return None, None
        return (
            format_utc_as_berlin(min_start),
            format_utc_as_berlin(max_end)
        )

    def _get_import_window(
        self,
        p_schedule_id: str
    ) -> tuple[
        datetime | None,
        datetime | None,
        datetime | None,
        int | None,
        str | None
    ]:
        has_history = self._shift_repository.has_import_history_for_schedule(
            p_schedule_id
        )
        if has_history:
            return None, None, None, None, None

        current_year = datetime.now().year
        since = datetime(current_year, 1, 1, 0, 0, 0)
        until = datetime(current_year, 12, 31, 23, 59, 59)
        date_anchor = since
        interval = 12
        interval_unit = "months"
        self._logger.info(
            "Erstimport für Schedule %s: since=%s until=%s date=%s interval=%s %s",
            p_schedule_id,
            since.isoformat() + "Z",
            until.isoformat() + "Z",
            date_anchor.isoformat() + "Z",
            interval,
            interval_unit
        )
        return since, until, date_anchor, interval, interval_unit
