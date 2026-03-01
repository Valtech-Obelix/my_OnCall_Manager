import  json
from    pathlib                                             import Path
from    datetime                                            import datetime, timedelta
from    math                                                import ceil
from    src.domain.import_result                            import  ImportResult
from    src.domain.shift                                    import  Shift
from    src.infrastructure.timezone_utils                   import  (
                                                                        format_utc_as_berlin,
                                                                        parse_utc_timestamp,
                                                                        BERLIN,
                                                                        UTC
                                                                    )
from    src.domain.exceptions                               import  (  OpsGenieApiException
                                                                     , OpsGenieAuthException
                                                                     , OpsGenieConnectionException
                                                                     , OpsGenieNotFoundException
                                                                    )

class OpsGenieService:
    SHIFT_BOUNDARY_HOUR = 1
    IMPORT_CHUNK_DAYS = 14

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

        # CR-005: Schichtplan-Referenzen unabhängig von shifts speichern.
        self._shift_repository.save_schedule_reference(
            p_schedule_id=p_schedule_id,
            p_schedule_name=p_schedule_name
        )

        since, until, _, _, _ = self._get_import_window(
            p_schedule_id
        )

        if since is None or until is None:
            return ImportResult(
                p_imported=imported,
                p_skipped=skipped,
                p_errors=errors
            )

        if since >= until:
            self._logger.warning(
                "Importfenster leer für Schedule %s: since=%s until=%s",
                p_schedule_id,
                since.isoformat() + "Z",
                until.isoformat() + "Z"
            )
            return ImportResult(
                p_imported=imported,
                p_skipped=skipped,
                p_errors=errors
            )

        chunk_windows = list(self._iter_import_windows(since, until))
        self._logger.info(
            "Import in %s Zeitfenster(n) für Schedule %s",
            len(chunk_windows),
            p_schedule_id
        )

        for chunk_since, chunk_until in chunk_windows:
            chunk_days = max(
                1,
                ceil((chunk_until - chunk_since).total_seconds() / 86400)
            )
            try:
                timeline = self._client.get_schedule_timeline(
                    p_schedule_id=p_schedule_id,
                    p_since=chunk_since,
                    p_until=chunk_until,
                    p_date=chunk_since,
                    p_interval=chunk_days,
                    p_interval_unit="days"
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
            period_count = sum(len(r.get("periods", [])) for r in rotations)
            self._logger.info(
                "Chunk import Schedule %s: since=%s until=%s interval=%s days -> periods=%s",
                p_schedule_id,
                chunk_since.isoformat() + "Z",
                chunk_until.isoformat() + "Z",
                chunk_days,
                period_count
            )

            self._enrich_opsgenie_ids_from_timeline(rotations)

            for rotation in rotations:
                periods = self._merge_fragmented_periods(rotation.get('periods', []))

                for period in periods:
                    if not self._period_start_in_window(period, chunk_since, chunk_until):
                        continue

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

                        recipient_id = recipient.get('id')

                        if not recipient_id:
                            self._log_skipped_period(
                                p_reason='missing recipient opsgenie_id',
                                p_rotation=rotation,
                                p_period=period
                            )
                            skipped += 1
                            continue

                        analyst = self._analyst_repository.find_by_opsgenie_id(
                            recipient_id
                        )

                        if not analyst:
                            self._log_skipped_period(
                                p_reason=f'no analyst found for opsgenie_id: {recipient_id}',
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

        return ImportResult(
            p_imported=imported,
            p_skipped=skipped,
            p_errors=errors
        )

    def _iter_import_windows(
        self,
        p_since: datetime,
        p_until: datetime
    ):
        cursor = p_since
        chunk_size = timedelta(days=self.IMPORT_CHUNK_DAYS)

        while cursor < p_until:
            chunk_until = min(cursor + chunk_size, p_until)
            yield cursor, chunk_until
            cursor = chunk_until

    def _merge_fragmented_periods(self, p_periods: list[dict]) -> list[dict]:
        merged: list[dict] = []
        by_key: dict[tuple[str, str, int], dict] = {}

        for period in p_periods:
            key = self._period_merge_key(period)
            if key is None:
                merged.append(period)
                continue

            current = by_key.get(key)
            if current is None:
                clone = dict(period)
                by_key[key] = clone
                merged.append(clone)
                continue

            current_start = parse_utc_timestamp(str(current.get("startDate")))
            current_end = parse_utc_timestamp(str(current.get("endDate")))
            period_start = parse_utc_timestamp(str(period.get("startDate")))
            period_end = parse_utc_timestamp(str(period.get("endDate")))

            if period_start < current_start:
                current["startDate"] = period.get("startDate")
            if period_end > current_end:
                current["endDate"] = period.get("endDate")

        return merged

    def _period_merge_key(self, p_period: dict) -> tuple[str, str, int] | None:
        recipient = p_period.get("recipient") or {}
        if recipient.get("type") != "user":
            return None

        recipient_id = (recipient.get("id") or "").strip().lower()
        start_date = p_period.get("startDate")
        end_date = p_period.get("endDate")
        if not recipient_id or not start_date or not end_date:
            return None

        start_local = parse_utc_timestamp(str(start_date)).astimezone(BERLIN)
        if start_local.hour < self.SHIFT_BOUNDARY_HOUR:
            display_day = start_local.date() - timedelta(days=1)
        else:
            display_day = start_local.date()

        shifted_hour = (start_local.hour - self.SHIFT_BOUNDARY_HOUR) % 24
        if shifted_hour < 8:
            slot_index = 0
        elif shifted_hour < 16:
            slot_index = 1
        else:
            slot_index = 2

        return recipient_id, display_day.isoformat(), slot_index

    def _period_start_in_window(
        self,
        p_period: dict,
        p_since: datetime,
        p_until: datetime
    ) -> bool:
        start_date = p_period.get("startDate")
        if not start_date:
            return False

        start_utc = parse_utc_timestamp(str(start_date)).astimezone(UTC).replace(tzinfo=None)
        return p_since <= start_utc < p_until

    def _enrich_opsgenie_ids_from_timeline(self, p_rotations: list[dict]) -> None:
        seen_pairs: set[tuple[str, str]] = set()

        for rotation in p_rotations:
            for period in rotation.get('periods', []):
                recipient = period.get('recipient') or {}
                if recipient.get('type') != 'user':
                    continue

                recipient_id = (recipient.get('id') or '').strip()
                recipient_email = (recipient.get('name') or '').strip()
                if not recipient_id:
                    continue

                if self._analyst_repository.find_by_opsgenie_id(recipient_id):
                    continue

                if not recipient_email:
                    self._logger.warning(
                        'OpsGenie ID %s konnte nicht automatisch zugeordnet werden '
                        '(recipient.name fehlt).',
                        recipient_id
                    )
                    continue

                marker = (recipient_id.lower(), recipient_email.lower())
                if marker in seen_pairs:
                    continue
                seen_pairs.add(marker)

                analyst = self._analyst_repository.find_by_email(recipient_email)
                if not analyst:
                    self._logger.warning(
                        'OpsGenie ID %s konnte nicht über E-Mail %s zugeordnet werden.',
                        recipient_id,
                        recipient_email
                    )
                    continue

                if (
                    analyst.opsgenie_id
                    and analyst.opsgenie_id.strip().lower() != recipient_id.lower()
                ):
                    self._logger.warning(
                        'OpsGenie ID Konflikt für Analyst %s (%s): bestehend=%s, neu=%s',
                        analyst.buchungsname,
                        analyst.email,
                        analyst.opsgenie_id,
                        recipient_id
                    )
                    continue

                self._analyst_repository.update_opsgenie_id(
                    p_id=analyst.id,
                    p_opsgenie_id=recipient_id
                )
                self._logger.info(
                    'OpsGenie ID automatisch ergänzt: %s -> %s (%s)',
                    recipient_email,
                    recipient_id,
                    analyst.buchungsname
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

    def get_next_import_start_local(self, p_schedule_id: str) -> str | None:
        schedule_id = (p_schedule_id or "").strip()
        if not schedule_id:
            return None
        since, _, _, _, _ = self._get_import_window(schedule_id)
        if since is None:
            return None
        return format_utc_as_berlin(since.isoformat() + "Z")

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
        now_local = self._current_local_time()
        last_complete_day_offset = 1 if now_local.hour >= self.SHIFT_BOUNDARY_HOUR else 2
        last_complete_day_local = (now_local - timedelta(days=last_complete_day_offset)).date()

        _, max_end = self._shift_repository.get_schedule_time_bounds(p_schedule_id)
        if max_end:
            since_dt = parse_utc_timestamp(max_end).astimezone(UTC) + timedelta(seconds=1)
            since = since_dt.replace(tzinfo=None)
        else:
            since = datetime(last_complete_day_local.year, 1, 1, 0, 0, 0)

        until_local = datetime(
            last_complete_day_local.year,
            last_complete_day_local.month,
            last_complete_day_local.day,
            self.SHIFT_BOUNDARY_HOUR,
            0,
            0,
            tzinfo=BERLIN
        ) + timedelta(days=1)
        until = until_local.astimezone(UTC).replace(tzinfo=None)
        date_anchor = None
        interval = None
        interval_unit = None
        self._logger.info(
            "Importfenster für Schedule %s: since=%s until=%s (letzter vollständiger Schichttag local=%s, max_end=%s)",
            p_schedule_id,
            since.isoformat() + "Z",
            until.isoformat() + "Z",
            last_complete_day_local.isoformat(),
            max_end
        )
        return since, until, date_anchor, interval, interval_unit

    def _current_local_time(self) -> datetime:
        return datetime.now(BERLIN)
