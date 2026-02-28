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
    def debug(self, *args, **kwargs):
        pass

    def info(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass


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
