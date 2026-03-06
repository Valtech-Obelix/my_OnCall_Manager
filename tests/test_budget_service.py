from datetime import date

import pytest

from src.infrastructure.database import Database
from src.infrastructure.budget_repository import BudgetRepository
from src.services.budget_service import BudgetService
from src.domain.exceptions import DomainException


def _create_service(tmp_path) -> tuple[BudgetService, Database]:
    db_path = tmp_path / "budget_service_test.db"
    database = Database(p_db_path=db_path)
    database.initialize_schema()
    repository = BudgetRepository(database.get_connection())
    return BudgetService(repository), database


def test_budget_source_crud_and_period_aggregation(tmp_path) -> None:
    service, database = _create_service(tmp_path)

    source_id = service.create_source("Kunde A")
    service.create_period(
        p_budget_source_id=source_id,
        p_gueltig_ab=date(2026, 1, 1),
        p_gueltig_bis=date(2026, 3, 31),
        p_betrag_eur=100.0,
    )
    service.create_period(
        p_budget_source_id=source_id,
        p_gueltig_ab=date(2026, 4, 1),
        p_betrag_eur=150.0,
    )

    assert service.get_budget_for_date(date(2026, 2, 15)) == 100.0
    assert service.get_budget_for_date(date(2026, 5, 10)) == 150.0

    periods = service.get_budget_periods(source_id)
    assert len(periods) == 2
    assert periods[0]["gueltig_ab"] == "2026-01-01"
    assert periods[0]["betrag_eur"] == 100.0

    timeline = service.get_budget_timeline(date(2026, 1, 1), date(2026, 4, 30))
    assert timeline == [
        {"from_date": "2026-01-01", "to_date": "2026-01-31", "label": "2026-01", "amount_eur": 100.0},
        {"from_date": "2026-02-01", "to_date": "2026-02-28", "label": "2026-02", "amount_eur": 100.0},
        {"from_date": "2026-03-01", "to_date": "2026-03-31", "label": "2026-03", "amount_eur": 100.0},
        {"from_date": "2026-04-01", "to_date": "2026-04-30", "label": "2026-04", "amount_eur": 150.0},
    ]

    service.set_source_active(p_source_id=source_id, p_is_active=False)
    assert service.get_budget_for_date(date(2026, 2, 15)) == 0.0

    service.delete_source(source_id)
    assert service.get_sources() == []

    database.close()


def test_budget_validation_rules(tmp_path) -> None:
    service, database = _create_service(tmp_path)

    source_id = service.create_source("Kunde B")

    with pytest.raises(DomainException, match="Enddatum darf nicht vor dem Startdatum"):
        service.create_period(
            p_budget_source_id=source_id,
            p_gueltig_ab=date(2026, 6, 1),
            p_gueltig_bis=date(2026, 5, 31),
            p_betrag_eur=50.0,
        )

    with pytest.raises(DomainException, match="Betrag darf nicht negativ"):
        service.create_period(
            p_budget_source_id=source_id,
            p_gueltig_ab=date(2026, 6, 1),
            p_betrag_eur=-5.0,
        )

    with pytest.raises(DomainException, match="Budgetquelle nicht gefunden"):
        service.create_period(
            p_budget_source_id=999,
            p_gueltig_ab=date(2026, 6, 1),
            p_betrag_eur=5.0,
        )

    database.close()
