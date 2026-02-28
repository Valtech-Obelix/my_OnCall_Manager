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
        CREATE TABLE incident_analyst (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vornamen TEXT NOT NULL,
            nachname TEXT NOT NULL,
            buchungsname TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            opsgenie_id TEXT,
            start_datum TEXT NOT NULL,
            ende_datum TEXT
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


def test_schedule_references_survive_clearing_shifts() -> None:
    repository = _create_repository()
    repository.save_schedule_reference(
        p_schedule_id="schedule-keep",
        p_schedule_name="Schichtplan Persistenz"
    )

    repository._connection.execute("DELETE FROM shifts")
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


def test_get_schedule_entries_returns_buchungsname_and_email() -> None:
    repository = _create_repository()
    repository._connection.execute(
        """
        INSERT INTO incident_analyst (
            id, vornamen, nachname, buchungsname, email, opsgenie_id, start_datum, ende_datum
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (1, "Thomas", "Ruf", "Thomas Ruf", "thomas.ruf@example.com", None, "2025-01-01", None)
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

    entries = repository.get_schedule_entries("schedule-42")

    assert len(entries) == 1
    assert entries[0]["buchungsname"] == "Thomas Ruf"
    assert entries[0]["email"] == "thomas.ruf@example.com"
