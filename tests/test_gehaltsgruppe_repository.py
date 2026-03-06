from datetime import date

from src.domain.gehaltsgruppe import Gehaltsgruppe, GehaltsgruppenBetrag
from src.infrastructure.database import Database
from src.infrastructure.gehaltsgruppe_repository import GehaltsgruppeRepository


def _create_repository(tmp_path) -> GehaltsgruppeRepository:
    db_path = tmp_path / "gehaltsgruppe_repository.db"
    database = Database(p_db_path=db_path)
    database.initialize_schema()
    return GehaltsgruppeRepository(database.get_connection())


def test_add_and_get_all(tmp_path) -> None:
    repository = _create_repository(tmp_path)

    created = repository.add(Gehaltsgruppe(p_id=None, p_bezeichnung="G1"))

    groups = repository.get_all()
    assert created.id is not None
    assert len(groups) == 1
    assert groups[0].bezeichnung == "G1"
    assert groups[0].oncall_location_id == "GER"


def test_get_betrag_am_stichtag_returns_valid_version(tmp_path) -> None:
    repository = _create_repository(tmp_path)
    group = repository.add(
        Gehaltsgruppe(
            p_id=None,
            p_bezeichnung="Nachtdienst",
            p_oncall_location_id="USA",
        )
    )
    assert group.oncall_location_id == "USA"

    repository.add_betrag(
        GehaltsgruppenBetrag(
            p_gehaltsgruppe_id=int(group.id),
            p_betrag=100.0,
            p_gueltig_ab=date(2026, 1, 1),
        )
    )
    repository.add_betrag(
        GehaltsgruppenBetrag(
            p_gehaltsgruppe_id=int(group.id),
            p_betrag=120.0,
            p_gueltig_ab=date(2026, 3, 1),
        )
    )

    assert repository.get_betrag_am_stichtag(int(group.id), date(2025, 12, 31)) is None
    assert repository.get_betrag_am_stichtag(int(group.id), date(2026, 2, 15)) == 100.0
    assert repository.get_betrag_am_stichtag(int(group.id), date(2026, 3, 1)) == 120.0


def test_get_betraege_returns_chronological_history(tmp_path) -> None:
    repository = _create_repository(tmp_path)
    group = repository.add(
        Gehaltsgruppe(
            p_id=None,
            p_bezeichnung="Tagdienst",
            p_oncall_location_id="FRA",
        )
    )
    assert group.oncall_location_id == "FRA"

    repository.add_betrag(
        GehaltsgruppenBetrag(
            p_gehaltsgruppe_id=int(group.id),
            p_betrag=90.0,
            p_gueltig_ab=date(2026, 2, 1),
        )
    )
    repository.add_betrag(
        GehaltsgruppenBetrag(
            p_gehaltsgruppe_id=int(group.id),
            p_betrag=95.0,
            p_gueltig_ab=date(2026, 4, 1),
        )
    )

    history = repository.get_betraege(int(group.id))

    assert history == [
        {"betrag": 90.0, "gueltig_ab": "2026-02-01"},
        {"betrag": 95.0, "gueltig_ab": "2026-04-01"},
    ]


def test_update_oncall_location(tmp_path) -> None:
    repository = _create_repository(tmp_path)
    group = repository.add(
        Gehaltsgruppe(
            p_id=None,
            p_bezeichnung="B",
            p_oncall_location_id="GER",
        )
    )

    repository.update_oncall_location(int(group.id), "USA")

    updated_groups = repository.get_all()
    assert len(updated_groups) == 1
    assert updated_groups[0].oncall_location_id == "USA"
