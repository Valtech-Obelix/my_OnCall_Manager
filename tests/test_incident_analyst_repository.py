import sqlite3
from datetime import date

from src.domain.incident_analyst import IncidentAnalyst
from src.infrastructure.incident_analyst_repository import IncidentAnalystRepository


def _create_repository() -> IncidentAnalystRepository:
    connection = sqlite3.connect(":memory:")
    connection.execute(
        """
        CREATE TABLE incident_analyst (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vornamen TEXT NOT NULL,
            nachname TEXT NOT NULL,
            buchungsname TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            start_datum TEXT NOT NULL,
            ende_datum TEXT
        )
        """
    )
    return IncidentAnalystRepository(connection)


def test_add_and_get_all_roundtrip() -> None:
    repository = _create_repository()

    created = repository.add(
        IncidentAnalyst(
            p_id=None,
            p_vornamen="Erika",
            p_nachname="Mustermann",
            p_email="erika@example.com",
            p_start_datum=date(2025, 2, 1),
        )
    )

    assert created.id is not None

    analysts = repository.get_all()
    assert len(analysts) == 1
    assert analysts[0].buchungsname == "Erika Mustermann"
    assert analysts[0].start_datum == date(2025, 2, 1)


def test_find_by_email_is_case_insensitive_and_parses_dates() -> None:
    repository = _create_repository()

    repository.add(
        IncidentAnalyst(
            p_id=None,
            p_vornamen="Lisa",
            p_nachname="Muster",
            p_email="lisa@example.com",
            p_start_datum=date(2024, 6, 1),
            p_ende_datum=date(2024, 12, 31),
        )
    )

    analyst = repository.find_by_email("LISA@EXAMPLE.COM")

    assert analyst is not None
    assert analyst.start_datum == date(2024, 6, 1)
    assert analyst.ende_datum == date(2024, 12, 31)
