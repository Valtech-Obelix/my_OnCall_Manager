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
    connection.execute(
        """
        CREATE TABLE schedule_registry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            schedule_id TEXT NOT NULL UNIQUE,
            schedule_name TEXT NOT NULL,
            last_used TEXT NOT NULL
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


def test_has_import_history_for_schedule() -> None:
    repository = _create_repository()
    repository.save_import_history(
        p_schedule_id="schedule-xyz",
        p_schedule_name="Schichtplan B"
    )

    assert repository.has_import_history_for_schedule("schedule-xyz") is True
    assert repository.has_import_history_for_schedule("schedule-none") is False


def test_schedule_references_survive_clearing_shifts_and_import_history() -> None:
    repository = _create_repository()
    repository.save_schedule_reference(
        p_schedule_id="schedule-keep",
        p_schedule_name="Schichtplan Persistenz"
    )

    repository._connection.execute("DELETE FROM shifts")
    repository._connection.execute("DELETE FROM import_history")
    repository._connection.commit()

    refs = repository.get_schedule_references()
    assert len(refs) == 1
    assert refs[0]["schedule_id"] == "schedule-keep"
    assert refs[0]["schedule_name"] == "Schichtplan Persistenz"


def test_get_schedule_time_bounds_for_schedule() -> None:
    repository = _create_repository()
    repository.save(
        Shift(
            p_id=None,
            p_analyst_id=1,
            p_project="A",
            p_schedule_id="schedule-42",
            p_start_time="2025-12-31T23:00:00Z",
            p_end_time="2026-01-01T08:00:00Z",
        )
    )
    repository.save(
        Shift(
            p_id=None,
            p_analyst_id=1,
            p_project="A",
            p_schedule_id="schedule-42",
            p_start_time="2026-01-02T00:00:00Z",
            p_end_time="2026-01-02T08:00:00Z",
        )
    )

    min_start, max_end = repository.get_schedule_time_bounds("schedule-42")
    assert min_start == "2025-12-31T23:00:00Z"
    assert max_end == "2026-01-02T08:00:00Z"
