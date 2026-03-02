import sqlite3
from datetime import datetime, timedelta, UTC

from src.domain.shift import Shift
from src.infrastructure.shift_repository import ShiftRepository
from src.infrastructure.timezone_utils import BERLIN


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
            oncall_location_id TEXT NOT NULL DEFAULT 'GER' CHECK (length(oncall_location_id) = 3),
            start_datum TEXT NOT NULL,
            ende_datum TEXT
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE rufbereitschaftsstandort (
            id TEXT PRIMARY KEY CHECK (length(id) = 3),
            name TEXT NOT NULL
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
    connection.execute(
        """
        CREATE TABLE app_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
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


def test_get_active_analyst_shift_counts_last_weeks_only_active() -> None:
    repository = _create_repository()
    in_window = (datetime.now(UTC) - timedelta(days=1)).replace(microsecond=0)
    in_window_end = in_window + timedelta(hours=8)
    out_window = (datetime.now(UTC) - timedelta(days=20)).replace(microsecond=0)
    out_window_end = out_window + timedelta(hours=8)
    repository._connection.execute(
        """
        INSERT INTO incident_analyst (
            id, vornamen, nachname, buchungsname, email, opsgenie_id, start_datum, ende_datum
        )
        VALUES
            (1, 'Max', 'Aktiv', 'Aktiv, Max', 'max.aktiv@example.com', NULL, '2025-01-01', NULL),
            (2, 'Ina', 'Inaktiv', 'Inaktiv, Ina', 'ina.inaktiv@example.com', NULL, '2025-01-01', '2025-12-31')
        """
    )
    repository.save(
        Shift(
            p_id=None,
            p_analyst_id=1,
            p_project="A",
            p_schedule_id="schedule-42",
            p_start_time=in_window.isoformat().replace("+00:00", "Z"),
            p_end_time=in_window_end.isoformat().replace("+00:00", "Z"),
        )
    )
    repository.save(
        Shift(
            p_id=None,
            p_analyst_id=2,
            p_project="A",
            p_schedule_id="schedule-42",
            p_start_time=in_window_end.isoformat().replace("+00:00", "Z"),
            p_end_time=(in_window_end + timedelta(hours=8)).isoformat().replace("+00:00", "Z"),
        )
    )
    repository.save(
        Shift(
            p_id=None,
            p_analyst_id=1,
            p_project="A",
            p_schedule_id="schedule-42",
            p_start_time=out_window.isoformat().replace("+00:00", "Z"),
            p_end_time=out_window_end.isoformat().replace("+00:00", "Z"),
        )
    )

    rows = repository.get_active_analyst_shift_counts_last_weeks(1)

    assert len(rows) == 1
    assert rows[0]["buchungsname"] == "Aktiv, Max"
    assert rows[0]["shift_count"] == 1


def test_settings_roundtrip() -> None:
    repository = _create_repository()
    assert repository.get_setting("last_shift_count_weeks") is None
    repository.set_setting("last_shift_count_weeks", "6")
    assert repository.get_setting("last_shift_count_weeks") == "6"


def test_get_location_shift_distribution_last_weeks() -> None:
    repository = _create_repository()
    now_local = datetime.now(BERLIN).replace(microsecond=0)
    current_monday_local = (now_local - timedelta(days=now_local.weekday())).replace(
        hour=12, minute=0, second=0
    )
    current_week_shift = (current_monday_local + timedelta(days=1)).astimezone(UTC)
    previous_week_shift = (current_monday_local - timedelta(days=1)).astimezone(UTC)
    old_shift = (current_monday_local - timedelta(days=120)).astimezone(UTC)

    repository._connection.execute(
        """
        INSERT INTO rufbereitschaftsstandort (id, name)
        VALUES
            ('GER', 'Deutschland'),
            ('USA', 'Vereinigte Staaten')
        """
    )
    repository._connection.execute(
        """
        INSERT INTO incident_analyst (
            id, vornamen, nachname, buchungsname, email, opsgenie_id, oncall_location_id, start_datum, ende_datum
        )
        VALUES
            (1, 'Max', 'Aktiv', 'Aktiv, Max', 'max.aktiv@example.com', NULL, 'GER', '2025-01-01', NULL),
            (2, 'Sue', 'West', 'West, Sue', 'sue.west@example.com', NULL, 'USA', '2025-01-01', NULL)
        """
    )

    repository.save(
        Shift(
            p_id=None,
            p_analyst_id=1,
            p_project="A",
            p_schedule_id="schedule-42",
            p_start_time=current_week_shift.isoformat().replace("+00:00", "Z"),
            p_end_time=(current_week_shift + timedelta(hours=8)).isoformat().replace("+00:00", "Z"),
        )
    )
    repository.save(
        Shift(
            p_id=None,
            p_analyst_id=2,
            p_project="A",
            p_schedule_id="schedule-42",
            p_start_time=previous_week_shift.isoformat().replace("+00:00", "Z"),
            p_end_time=(previous_week_shift + timedelta(hours=8)).isoformat().replace("+00:00", "Z"),
        )
    )
    repository.save(
        Shift(
            p_id=None,
            p_analyst_id=1,
            p_project="A",
            p_schedule_id="schedule-42",
            p_start_time=old_shift.isoformat().replace("+00:00", "Z"),
            p_end_time=(old_shift + timedelta(hours=8)).isoformat().replace("+00:00", "Z"),
        )
    )

    result = repository.get_location_shift_distribution_last_weeks(2)

    assert len(result["weeks"]) == 2
    assert result["locations"] == [
        {"location_id": "GER", "location_name": "Deutschland"},
        {"location_id": "USA", "location_name": "Vereinigte Staaten"},
    ]
    counts_week_1 = result["weeks"][0]["counts"]
    counts_week_2 = result["weeks"][1]["counts"]
    assert isinstance(counts_week_1, dict)
    assert isinstance(counts_week_2, dict)
    assert sum(int(v) for v in counts_week_1.values()) == 1
    assert sum(int(v) for v in counts_week_2.values()) == 1
