from datetime import date

import pytest

from src.domain.exceptions import DomainException
from src.domain.incident_analyst import IncidentAnalyst
from src.services.incident_analyst_service import IncidentAnalystService


class _FakeRepository:
    def __init__(self):
        self._store = {
            1: IncidentAnalyst(
                p_id=1,
                p_vornamen="Max",
                p_nachname="Muster",
                p_email="max@example.com",
                p_start_datum=date(2025, 1, 1),
                p_oncall_location_id="GER",
            )
        }

    def find_by_id(self, p_id: int):
        return self._store.get(p_id)

    def update(self, p_analyst: IncidentAnalyst):
        self._store[p_analyst.id] = p_analyst
        return p_analyst

    def get_all(self):
        return list(self._store.values())

    def update_end_date(self, p_id: int, p_ende_datum):
        analyst = self._store[p_id]
        self._store[p_id] = IncidentAnalyst(
            p_id=analyst.id,
            p_vornamen=analyst.vornamen,
            p_nachname=analyst.nachname,
            p_email=analyst.email,
            p_start_datum=analyst.start_datum,
            p_ende_datum=p_ende_datum,
            p_opsgenie_id=analyst.opsgenie_id,
            p_oncall_location_id=analyst.oncall_location_id,
        )


def test_update_changes_incident_analyst_data() -> None:
    repository = _FakeRepository()
    service = IncidentAnalystService(repository)

    updated = service.update(
        p_id=1,
        p_vornamen="Thomas",
        p_nachname="Ruf",
        p_email="thomas.ruf@example.com",
        p_start_datum=date(2025, 2, 1),
        p_ende_datum=None,
        p_opsgenie_id="325b3fbf-cbb2-4724-abe1-4fb488655ede",
        p_oncall_location_id="USA",
    )

    assert updated.vornamen == "Thomas"
    assert updated.nachname == "Ruf"
    assert updated.email == "thomas.ruf@example.com"
    assert updated.opsgenie_id == "325b3fbf-cbb2-4724-abe1-4fb488655ede"
    assert updated.oncall_location_id == "USA"
    assert updated.start_datum == date(2025, 2, 1)


def test_update_raises_when_analyst_does_not_exist() -> None:
    repository = _FakeRepository()
    service = IncidentAnalystService(repository)

    with pytest.raises(DomainException, match="nicht gefunden"):
        service.update(
            p_id=999,
            p_vornamen="A",
            p_nachname="B",
            p_email="a@example.com",
            p_start_datum=date(2025, 1, 1),
        )
