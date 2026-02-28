import  json
from    pathlib                                             import Path
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
        p_logger,
        p_last_import_dump_file: str = 'debug/last_opsgenie_import.json'
    ):
        self._client = p_client
        self._shift_repository = p_shift_repository
        self._analyst_repository = p_analyst_repository
        self._logger = p_logger
        self._last_import_dump_file = Path(p_last_import_dump_file)

    def import_schedule(
        self,
        p_schedule_id: str,
        p_schedule_name: str,
        p_dump_full_json: bool = False
    ) -> ImportResult:

        imported = 0
        skipped = 0
        errors = 0

        # CR-005: Schichtplan-Referenzen unabhängig von shifts/import_history speichern.
        self._shift_repository.save_schedule_reference(
            p_schedule_id=p_schedule_id,
            p_schedule_name=p_schedule_name
        )

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
            if p_dump_full_json:
                self._write_last_import_json_dump(timeline)

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
                        self._log_skipped_period(
                            p_reason='missing recipient',
                            p_rotation=rotation,
                            p_period=period
                        )
                        skipped += 1
                        continue

                    if recipient.get('type') != 'user':
                        self._log_skipped_period(
                            p_reason='recipient is not a user',
                            p_rotation=rotation,
                            p_period=period
                        )
                        skipped += 1
                        continue

                    email = recipient.get('name')

                    if not email:
                        self._log_skipped_period(
                            p_reason='missing recipient email',
                            p_rotation=rotation,
                            p_period=period
                        )
                        skipped += 1
                        continue

                    analyst = self._analyst_repository.find_by_email(email)

                    if not analyst:
                        self._log_skipped_period(
                            p_reason=f'no analyst found for email: {email}',
                            p_rotation=rotation,
                            p_period=period
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
                        self._log_skipped_period(
                            p_reason='duplicate shift (already exists)',
                            p_rotation=rotation,
                            p_period=period
                        )
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

    def _log_skipped_period(
        self,
        p_reason: str,
        p_rotation: dict,
        p_period: dict
    ) -> None:
        start_date = p_period.get('startDate')
        end_date = p_period.get('endDate')
        snippet = {
            'rotation': {
                'id': p_rotation.get('id'),
                'name': p_rotation.get('name')
            },
            'period': p_period
        }
        self._logger.warning(
            'Skipped schedule entry: %s | startDate=%s | endDate=%s',
            p_reason,
            start_date,
            end_date
        )
        self._logger.debug(
            'Skipped schedule entry snippet: %s',
            json.dumps(snippet, ensure_ascii=False)
        )

    def get_schedule_references(self) -> list[dict[str, str]]:
        return self._shift_repository.get_schedule_references()

    def _write_last_import_json_dump(self, p_timeline: dict) -> None:
        self._last_import_dump_file.parent.mkdir(parents=True, exist_ok=True)
        self._last_import_dump_file.write_text(
            json.dumps(p_timeline, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        self._logger.info(
            'Vollständiger OpsGenie JSON-Dump gespeichert: %s',
            self._last_import_dump_file
        )

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
