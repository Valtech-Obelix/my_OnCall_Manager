import sqlite3

from src.domain.shift import Shift
from src.infrastructure.shift_repository import ShiftRepository


def _create_repository() -> ShiftRepository:
    connection = sqlite3.connect(":memory:")
    connection.execute(
        """
        CREATE TABLE shifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analyst_id INTEGER NOT NULL,
            project TEXT NOT NULL,
            schedule_id TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            UNIQUE (analyst_id, schedule_id, start_time, end_time)
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE import_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL UNIQUE,
            last_import TEXT NOT NULL
        )
        """
    )
    return ShiftRepository(connection)


def test_save_returns_false_for_duplicate_shift() -> None:
    repository = _create_repository()
    shift = Shift(
        p_id=None,
        p_analyst_id=1,
        p_project="A",
        p_schedule_id="schedule-1",
        p_start_time="2026-02-27T08:00:00Z",
        p_end_time="2026-02-27T16:00:00Z",
    )

    assert repository.save(shift) is True
    assert repository.save(shift) is False


def test_import_history_roundtrip() -> None:
    repository = _create_repository()
    repository.save_import_history(
        p_schedule_id="schedule-123",
        p_schedule_name="Schichtplan A"
    )

    history = repository.get_import_history()

    assert len(history) == 1
    assert history[0]["schedule_id"] == "schedule-123"
    assert history[0]["schedule_name"] == "Schichtplan A"
    assert history[0]["last_import"]
