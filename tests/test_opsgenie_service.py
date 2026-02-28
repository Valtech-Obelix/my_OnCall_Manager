from datetime import datetime

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
    def __init__(self, has_history: bool):
        self._has_history = has_history
        self.saved_history = []
        self.saved_references = []

    def has_import_history_for_schedule(self, p_schedule_id: str) -> bool:
        return self._has_history

    def save_import_history(self, p_schedule_id: str, p_schedule_name: str) -> None:
        self.saved_history.append((p_schedule_id, p_schedule_name))

    def save_schedule_reference(self, p_schedule_id: str, p_schedule_name: str) -> None:
        self.saved_references.append((p_schedule_id, p_schedule_name))

    def get_schedule_references(self):
        return []

    def save(self, p_shift):
        return True


class _FakeAnalystRepository:
    def find_by_email(self, p_email: str):
        return None


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


def test_first_import_uses_since_january_first_current_year() -> None:
    client = _FakeClient()
    shift_repository = _FakeShiftRepository(has_history=False)
    service = OpsGenieService(
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
    assert since == datetime(datetime.now().year, 1, 1, 0, 0, 0)
    assert until == datetime(datetime.now().year, 12, 31, 23, 59, 59)
    assert date_anchor == datetime(datetime.now().year, 1, 1, 0, 0, 0)
    assert interval == 12
    assert interval_unit == "months"


def test_follow_up_import_uses_no_since_filter() -> None:
    client = _FakeClient()
    shift_repository = _FakeShiftRepository(has_history=True)
    service = OpsGenieService(
        p_client=client,
        p_shift_repository=shift_repository,
        p_analyst_repository=_FakeAnalystRepository(),
        p_logger=_FakeLogger(),
    )

    service.import_schedule("schedule-1", "Schichtplan A")

    assert len(client.calls) == 1
    assert shift_repository.saved_references == [("schedule-1", "Schichtplan A")]
    assert client.calls[0]["since"] is None
    assert client.calls[0]["until"] is None
    assert client.calls[0]["date"] is None
    assert client.calls[0]["interval"] is None
    assert client.calls[0]["interval_unit"] is None


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
        p_shift_repository=_FakeShiftRepository(has_history=True),
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
        p_shift_repository=_FakeShiftRepository(has_history=True),
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
