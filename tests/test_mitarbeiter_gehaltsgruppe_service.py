from datetime import date

import pytest

from src.domain.exceptions import DomainException
from src.domain.incident_analyst import IncidentAnalyst
from src.infrastructure.database import Database
from src.domain.gehaltsgruppe import Gehaltsgruppe
from src.infrastructure.gehaltsgruppe_repository import GehaltsgruppeRepository
from src.infrastructure.incident_analyst_repository import IncidentAnalystRepository
from src.services.mitarbeiter_gehaltsgruppe_service import MitarbeiterGehaltsgruppeService


def _setup(tmp_path):
    db_path = tmp_path / "mitarbeiter_gehaltsgruppe_service.db"
    database = Database(p_db_path=db_path)
    database.initialize_schema()
    analyst_repository = IncidentAnalystRepository(database.get_connection())
    gehaltsgruppe_repository = GehaltsgruppeRepository(database.get_connection())
    service = MitarbeiterGehaltsgruppeService(
        p_analyst_repository=analyst_repository,
        p_gehaltsgruppe_repository=gehaltsgruppe_repository,
    )
    return analyst_repository, gehaltsgruppe_repository, service


def _create_analyst(repository: IncidentAnalystRepository) -> int:
    analyst = repository.add(
        IncidentAnalyst(
            p_id=None,
            p_vornamen="Max",
            p_nachname="Muster",
            p_email="max.muster@example.com",
            p_start_datum=date(2026, 1, 1),
        )
    )
    return int(analyst.id)


def _create_group(repository: GehaltsgruppeRepository, p_name: str) -> int:
    created = repository.add(
        Gehaltsgruppe(
            p_id=None,
            p_bezeichnung=p_name,
        )
    )
    return int(created.id)


def test_assign_creates_first_assignment(tmp_path) -> None:
    analyst_repo, group_repo, service = _setup(tmp_path)
    mitarbeiter_id = _create_analyst(analyst_repo)
    group_id = _create_group(group_repo, "A")

    service.assign(
        p_mitarbeiter_id=mitarbeiter_id,
        p_gehaltsgruppe_id=group_id,
        p_gueltig_ab=date(2026, 1, 1),
        p_gueltig_bis=None,
    )

    assignments = service.get_assignments(mitarbeiter_id)
    assert len(assignments) == 1
    assert assignments[0]["gehaltsgruppe_id"] == group_id


def test_assign_rejects_overlapping_periods(tmp_path) -> None:
    analyst_repo, group_repo, service = _setup(tmp_path)
    mitarbeiter_id = _create_analyst(analyst_repo)
    group_a = _create_group(group_repo, "A")
    group_b = _create_group(group_repo, "B")

    service.assign(
        p_mitarbeiter_id=mitarbeiter_id,
        p_gehaltsgruppe_id=group_a,
        p_gueltig_ab=date(2026, 1, 1),
        p_gueltig_bis=date(2026, 6, 30),
    )

    with pytest.raises(DomainException, match="ueberlappt"):
        service.assign(
            p_mitarbeiter_id=mitarbeiter_id,
            p_gehaltsgruppe_id=group_b,
            p_gueltig_ab=date(2026, 6, 1),
            p_gueltig_bis=date(2026, 12, 31),
        )


def test_assign_allows_correction_same_period(tmp_path) -> None:
    analyst_repo, group_repo, service = _setup(tmp_path)
    mitarbeiter_id = _create_analyst(analyst_repo)
    group_a = _create_group(group_repo, "A")
    group_b = _create_group(group_repo, "B")

    service.assign(
        p_mitarbeiter_id=mitarbeiter_id,
        p_gehaltsgruppe_id=group_a,
        p_gueltig_ab=date(2026, 1, 1),
        p_gueltig_bis=date(2026, 12, 31),
    )
    service.assign(
        p_mitarbeiter_id=mitarbeiter_id,
        p_gehaltsgruppe_id=group_b,
        p_gueltig_ab=date(2026, 1, 1),
        p_gueltig_bis=date(2026, 12, 31),
    )

    assignments = service.get_assignments(mitarbeiter_id)
    assert len(assignments) == 1
    assert assignments[0]["gehaltsgruppe_id"] == group_b


def test_get_assignment_at_returns_matching_period(tmp_path) -> None:
    analyst_repo, group_repo, service = _setup(tmp_path)
    mitarbeiter_id = _create_analyst(analyst_repo)
    group_a = _create_group(group_repo, "A")
    group_b = _create_group(group_repo, "B")

    service.assign(
        p_mitarbeiter_id=mitarbeiter_id,
        p_gehaltsgruppe_id=group_a,
        p_gueltig_ab=date(2026, 1, 1),
        p_gueltig_bis=date(2026, 6, 30),
    )
    service.assign(
        p_mitarbeiter_id=mitarbeiter_id,
        p_gehaltsgruppe_id=group_b,
        p_gueltig_ab=date(2026, 7, 1),
        p_gueltig_bis=None,
    )

    current = service.get_assignment_at(mitarbeiter_id, date(2026, 8, 1))
    assert current is not None
    assert current["gehaltsgruppe_id"] == group_b


def test_assign_switch_closes_previous_open_period(tmp_path) -> None:
    analyst_repo, group_repo, service = _setup(tmp_path)
    mitarbeiter_id = _create_analyst(analyst_repo)
    group_a = _create_group(group_repo, "A")
    group_b = _create_group(group_repo, "B")

    service.assign(
        p_mitarbeiter_id=mitarbeiter_id,
        p_gehaltsgruppe_id=group_a,
        p_gueltig_ab=date(2026, 1, 1),
        p_gueltig_bis=None,
    )
    service.assign(
        p_mitarbeiter_id=mitarbeiter_id,
        p_gehaltsgruppe_id=group_b,
        p_gueltig_ab=date(2026, 3, 1),
        p_gueltig_bis=None,
    )

    assignments = service.get_assignments(mitarbeiter_id)
    assert len(assignments) == 2
    assert assignments[0]["gehaltsgruppe_id"] == group_a
    assert assignments[0]["gueltig_ab"] == "2026-01-01"
    assert assignments[0]["gueltig_bis"] == "2026-02-28"
    assert assignments[1]["gehaltsgruppe_id"] == group_b
    assert assignments[1]["gueltig_ab"] == "2026-03-01"
    assert assignments[1]["gueltig_bis"] == ""
