from datetime import date

import pytest

from src.domain.exceptions import DomainException
from src.infrastructure.database import Database
from src.infrastructure.gehaltsgruppe_repository import GehaltsgruppeRepository
from src.services.gehaltsgruppe_service import GehaltsgruppeService


def _create_service(tmp_path) -> GehaltsgruppeService:
    db_path = tmp_path / "gehaltsgruppe_service.db"
    database = Database(p_db_path=db_path)
    database.initialize_schema()
    repository = GehaltsgruppeRepository(database.get_connection())
    return GehaltsgruppeService(repository)


def test_create_gehaltsgruppe_requires_gueltig_ab(tmp_path) -> None:
    service = _create_service(tmp_path)

    with pytest.raises(DomainException, match="Gueltig-ab-Datum"):
        service.create(
            p_bezeichnung="Bereitschaft",
            p_betrag=100.0,
            p_gueltig_ab=None,
        )


def test_update_betrag_requires_gueltig_ab_without_prefill_default(tmp_path) -> None:
    service = _create_service(tmp_path)
    group = service.create(
        p_bezeichnung="Bereitschaft",
        p_betrag=100.0,
        p_gueltig_ab=date(2026, 1, 1),
    )

    with pytest.raises(DomainException, match="Gueltig-ab-Datum"):
        service.update_betrag(
            p_group_id=int(group.id),
            p_betrag=110.0,
            p_gueltig_ab=None,
        )


def test_get_betrag_am_stichtag_returns_version_for_date(tmp_path) -> None:
    service = _create_service(tmp_path)
    group = service.create(
        p_bezeichnung="Wochenende",
        p_betrag=150.0,
        p_gueltig_ab=date(2026, 1, 1),
    )
    service.update_betrag(
        p_group_id=int(group.id),
        p_betrag=175.0,
        p_gueltig_ab=date(2026, 5, 1),
    )

    assert service.get_betrag_am_stichtag(int(group.id), date(2026, 2, 1)) == 150.0
    assert service.get_betrag_am_stichtag(int(group.id), date(2026, 5, 1)) == 175.0


def test_update_betrag_rejects_duplicate_effective_date(tmp_path) -> None:
    service = _create_service(tmp_path)
    group = service.create(
        p_bezeichnung="Feiertag",
        p_betrag=180.0,
        p_gueltig_ab=date(2026, 1, 1),
    )

    with pytest.raises(DomainException, match="gueltig-ab-Datum"):
        service.update_betrag(
            p_group_id=int(group.id),
            p_betrag=190.0,
            p_gueltig_ab=date(2026, 1, 1),
        )


def test_create_gehaltsgruppe_uses_oncall_location(tmp_path) -> None:
    service = _create_service(tmp_path)
    group = service.create(
        p_bezeichnung="Night",
        p_betrag=120.0,
        p_gueltig_ab=date(2026, 1, 1),
        p_oncall_location_id="USA",
    )

    all_groups = service.get_all()
    assert len(all_groups) == 1
    assert all_groups[0].oncall_location_id == "USA"


def test_update_gehaltsgruppe_oncall_location(tmp_path) -> None:
    service = _create_service(tmp_path)
    group = service.create(
        p_bezeichnung="Tag",
        p_betrag=200.0,
        p_gueltig_ab=date(2026, 1, 1),
        p_oncall_location_id="GER",
    )

    service.update_oncall_location(p_group_id=int(group.id), p_oncall_location_id="FRA")

    updated = service.get_all()
    assert len(updated) == 1
    assert updated[0].oncall_location_id == "FRA"


def test_update_gehaltsgruppe_oncall_location_rejects_invalid_input(tmp_path) -> None:
    service = _create_service(tmp_path)
    group = service.create(
        p_bezeichnung="Nacht",
        p_betrag=250.0,
        p_gueltig_ab=date(2026, 1, 1),
    )

    with pytest.raises(DomainException, match="Standortkennung"):
        service.update_oncall_location(
            p_group_id=int(group.id),
            p_oncall_location_id="DE",
        )
