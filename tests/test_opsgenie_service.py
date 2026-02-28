from datetime import datetime

from src.infrastructure.timezone_utils import BERLIN
from src.services.opsgenie_service import OpsGenieService


class _FakeClient:
    def __init__(self):
        self.calls = []

    def get_schedule_timeline(
        self,
        p_schedule_id: str,
        p_since=None,
        p_until=None,
        p_date=None,
        p_interval=None,
        p_interval_unit=None
    ):
        self.calls.append(
            {
                "schedule_id": p_schedule_id,
                "since": p_since,
                "until": p_until,
                "date": p_date,
                "interval": p_interval,
                "interval_unit": p_interval_unit,
            }
        )
        return {"data": {"finalTimeline": {"rotations": []}}}


class _FakeShiftRepository:
    def __init__(self, p_max_end: str | None = None):
        self._max_end = p_max_end
        self.saved_references = []

    def save_schedule_reference(self, p_schedule_id: str, p_schedule_name: str) -> None:
        self.saved_references.append((p_schedule_id, p_schedule_name))

    def get_schedule_references(self):
        return []

    def save(self, p_shift):
        return True

    def get_schedule_time_bounds(self, p_schedule_id: str):
        return None, self._max_end


class _FakeAnalystRepository:
    def __init__(self):
        self.by_opsgenie_id = {}
        self.by_email = {}
        self.updated_opsgenie_ids = []

    def find_by_opsgenie_id(self, p_opsgenie_id: str):
        return self.by_opsgenie_id.get((p_opsgenie_id or "").lower())

    def find_by_email(self, p_email: str):
        return self.by_email.get((p_email or "").lower())

    def update_opsgenie_id(self, p_id: int, p_opsgenie_id: str):
        self.updated_opsgenie_ids.append((p_id, p_opsgenie_id))
        target = None
        for analyst in self.by_email.values():
            if analyst.id == p_id:
                target = analyst
                break
        if target is not None:
            target.opsgenie_id = p_opsgenie_id
            self.by_opsgenie_id[p_opsgenie_id.lower()] = target


class _FakeLogger:
    def __init__(self):
        self.debug_messages = []
        self.info_messages = []
        self.warning_messages = []
        self.error_messages = []

    @staticmethod
    def _render(message, *args):
        if args:
            return message % args
        return message

    def debug(self, *args, **kwargs):
        self.debug_messages.append(self._render(*args))

    def info(self, *args, **kwargs):
        self.info_messages.append(self._render(*args))

    def warning(self, *args, **kwargs):
        self.warning_messages.append(self._render(*args))

    def error(self, *args, **kwargs):
        self.error_messages.append(self._render(*args))


class _FakeTimelineClient(_FakeClient):
    def __init__(self, p_timeline):
        super().__init__()
        self._timeline = p_timeline

    def get_schedule_timeline(
        self,
        p_schedule_id: str,
        p_since=None,
        p_until=None,
        p_date=None,
        p_interval=None,
        p_interval_unit=None
    ):
        super().get_schedule_timeline(
            p_schedule_id=p_schedule_id,
            p_since=p_since,
            p_until=p_until,
            p_date=p_date,
            p_interval=p_interval,
            p_interval_unit=p_interval_unit
        )
        return self._timeline


class _FixedNowOpsGenieService(OpsGenieService):
    def __init__(self, p_now_local: datetime, **kwargs):
        super().__init__(**kwargs)
        self._now_local = p_now_local

    def _current_local_time(self) -> datetime:
        return self._now_local


def test_import_before_01_00_uses_yesterday_minus_one_day_as_last_complete_day() -> None:
    client = _FakeClient()
    shift_repository = _FakeShiftRepository(
        p_max_end="2026-02-15T16:00:00Z"
    )
    service = _FixedNowOpsGenieService(
        p_now_local=datetime(2026, 3, 1, 0, 30, 0, tzinfo=BERLIN),
        p_client=client,
        p_shift_repository=shift_repository,
        p_analyst_repository=_FakeAnalystRepository(),
        p_logger=_FakeLogger(),
    )

    service.import_schedule("schedule-1", "Schichtplan A")

    assert len(client.calls) == 1
    assert shift_repository.saved_references == [("schedule-1", "Schichtplan A")]
    since = client.calls[0]["since"]
    until = client.calls[0]["until"]
    date_anchor = client.calls[0]["date"]
    interval = client.calls[0]["interval"]
    interval_unit = client.calls[0]["interval_unit"]
    assert since == datetime(2026, 2, 15, 16, 0, 1)
    assert until == datetime(2026, 2, 28, 0, 0, 0)
    assert date_anchor == datetime(2026, 2, 15, 16, 0, 1)
    assert interval == 12
    assert interval_unit == "months"


def test_import_after_01_00_uses_previous_day_as_last_complete_day() -> None:
    client = _FakeClient()
    shift_repository = _FakeShiftRepository(
        p_max_end="2026-02-28T16:00:00Z"
    )
    service = _FixedNowOpsGenieService(
        p_now_local=datetime(2026, 3, 1, 1, 5, 0, tzinfo=BERLIN),
        p_client=client,
        p_shift_repository=shift_repository,
        p_analyst_repository=_FakeAnalystRepository(),
        p_logger=_FakeLogger(),
    )

    service.import_schedule("schedule-1", "Schichtplan A")

    assert len(client.calls) == 1
    assert shift_repository.saved_references == [("schedule-1", "Schichtplan A")]
    since = client.calls[0]["since"]
    until = client.calls[0]["until"]
    date_anchor = client.calls[0]["date"]
    interval = client.calls[0]["interval"]
    interval_unit = client.calls[0]["interval_unit"]
    assert since == datetime(2026, 2, 28, 16, 0, 1)
    assert until == datetime(2026, 3, 1, 0, 0, 0)
    assert date_anchor == datetime(2026, 2, 28, 16, 0, 1)
    assert interval == 12
    assert interval_unit == "months"


def test_import_without_existing_shifts_starts_at_january_first() -> None:
    client = _FakeClient()
    shift_repository = _FakeShiftRepository(p_max_end=None)
    service = _FixedNowOpsGenieService(
        p_now_local=datetime(2026, 3, 1, 1, 5, 0, tzinfo=BERLIN),
        p_client=client,
        p_shift_repository=shift_repository,
        p_analyst_repository=_FakeAnalystRepository(),
        p_logger=_FakeLogger(),
    )

    service.import_schedule("schedule-1", "Schichtplan A")

    assert len(client.calls) == 1
    assert client.calls[0]["since"] == datetime(2026, 1, 1, 0, 0, 0)


def test_skipped_entries_log_reason_and_json_snippet() -> None:
    timeline = {
        "data": {
            "finalTimeline": {
                "rotations": [
                    {
                        "id": "rotation-1",
                        "name": "Primary",
                        "periods": [
                            {
                                "startDate": "2026-02-27T08:00:00Z",
                                "endDate": "2026-02-27T16:00:00Z",
                            }
                        ],
                    }
                ]
            }
        }
    }
    client = _FakeTimelineClient(timeline)
    logger = _FakeLogger()
    service = OpsGenieService(
        p_client=client,
        p_shift_repository=_FakeShiftRepository(),
        p_analyst_repository=_FakeAnalystRepository(),
        p_logger=logger,
    )

    result = service.import_schedule("schedule-1", "Schichtplan A")

    assert result.skipped == 1
    assert len(logger.warning_messages) == 1
    assert "Skipped schedule entry: missing recipient" in logger.warning_messages[0]
    assert "startDate=2026-02-27T08:00:00Z" in logger.warning_messages[0]
    assert "endDate=2026-02-27T16:00:00Z" in logger.warning_messages[0]
    assert all("snippet=" not in msg for msg in logger.warning_messages)
    assert len(logger.debug_messages) == 1
    assert "Skipped schedule entry snippet:" in logger.debug_messages[0]
    assert '"rotation": {"id": "rotation-1", "name": "Primary"}' in logger.debug_messages[0]
    assert '"period": {"startDate": "2026-02-27T08:00:00Z", "endDate": "2026-02-27T16:00:00Z"}' in logger.debug_messages[0]
    assert all("RAW OPSGENIE RESPONSE" not in msg for msg in logger.debug_messages)


def test_optional_full_json_dump_writes_last_import_file(tmp_path) -> None:
    timeline = {
        "data": {
            "finalTimeline": {
                "rotations": []
            }
        }
    }
    client = _FakeTimelineClient(timeline)
    logger = _FakeLogger()
    dump_file = tmp_path / "debug" / "last_opsgenie_import.json"
    service = OpsGenieService(
        p_client=client,
        p_shift_repository=_FakeShiftRepository(),
        p_analyst_repository=_FakeAnalystRepository(),
        p_logger=logger,
        p_last_import_dump_file=str(dump_file),
    )

    service.import_schedule(
        "schedule-1",
        "Schichtplan A",
        p_dump_full_json=True
    )

    assert dump_file.exists() is True
    assert '"rotations": []' in dump_file.read_text(encoding="utf-8")
    assert any(
        "Vollständiger OpsGenie JSON-Dump gespeichert:" in msg
        for msg in logger.info_messages
    )


class _SimpleAnalyst:
    def __init__(self, p_id, p_email, p_buchungsname, p_opsgenie_id=None):
        self.id = p_id
        self.email = p_email
        self.buchungsname = p_buchungsname
        self.opsgenie_id = p_opsgenie_id


def test_precheck_enriches_opsgenie_id_by_email_before_import() -> None:
    timeline = {
        "data": {
            "finalTimeline": {
                "rotations": [
                    {
                        "id": "rotation-1",
                        "name": "Primary",
                        "periods": [
                            {
                                "startDate": "2026-02-27T08:00:00Z",
                                "endDate": "2026-02-27T16:00:00Z",
                                "recipient": {
                                    "id": "3fb94b87-755b-4bc1-a4bf-fdf79f445dda",
                                    "type": "user",
                                    "name": "alexander.hergenroeder@valtech-mobility.com",
                                },
                            }
                        ],
                    }
                ]
            }
        }
    }
    client = _FakeTimelineClient(timeline)
    analysts = _FakeAnalystRepository()
    analysts.by_email["alexander.hergenroeder@valtech-mobility.com"] = _SimpleAnalyst(
        p_id=1,
        p_email="alexander.hergenroeder@valtech-mobility.com",
        p_buchungsname="Alexander Hergenroeder",
        p_opsgenie_id=None,
    )
    shift_repository = _FakeShiftRepository()
    service = OpsGenieService(
        p_client=client,
        p_shift_repository=shift_repository,
        p_analyst_repository=analysts,
        p_logger=_FakeLogger(),
    )

    result = service.import_schedule("schedule-1", "Schichtplan A")

    assert (1, "3fb94b87-755b-4bc1-a4bf-fdf79f445dda") in analysts.updated_opsgenie_ids
    assert result.imported == 1
    assert result.skipped == 0


def test_precheck_does_not_override_conflicting_opsgenie_id() -> None:
    timeline = {
        "data": {
            "finalTimeline": {
                "rotations": [
                    {
                        "id": "rotation-1",
                        "name": "Primary",
                        "periods": [
                            {
                                "startDate": "2026-02-27T08:00:00Z",
                                "endDate": "2026-02-27T16:00:00Z",
                                "recipient": {
                                    "id": "new-id-123",
                                    "type": "user",
                                    "name": "alexander.hergenroeder@valtech-mobility.com",
                                },
                            }
                        ],
                    }
                ]
            }
        }
    }
    client = _FakeTimelineClient(timeline)
    analysts = _FakeAnalystRepository()
    analysts.by_email["alexander.hergenroeder@valtech-mobility.com"] = _SimpleAnalyst(
        p_id=1,
        p_email="alexander.hergenroeder@valtech-mobility.com",
        p_buchungsname="Alexander Hergenroeder",
        p_opsgenie_id="old-id-999",
    )
    service = OpsGenieService(
        p_client=client,
        p_shift_repository=_FakeShiftRepository(),
        p_analyst_repository=analysts,
        p_logger=_FakeLogger(),
    )

    result = service.import_schedule("schedule-1", "Schichtplan A")

    assert analysts.updated_opsgenie_ids == []
    assert result.skipped == 1
