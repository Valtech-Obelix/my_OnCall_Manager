from datetime import date

import pytest

from src.domain.exceptions import DomainException
from src.domain.incident_analyst import IncidentAnalyst
from src.services.mitarbeiter_aktivierung_service import MitarbeiterAktivierungService


class _FakeRepository:
    def __init__(self):
        self._analysts = {
            1: IncidentAnalyst(
                p_id=1,
                p_vornamen="Olaf",
                p_nachname="Henke",
                p_email="olaf@example.com",
                p_start_datum=date(2026, 1, 1),
            )
        }
        self._periods: dict[int, list[dict[str, str | int]]] = {1: []}

    def find_by_id(self, p_id: int):
        return self._analysts.get(p_id)

    def get_activation_periods(self, p_mitarbeiter_id: int):
        return list(self._periods.get(p_mitarbeiter_id, []))

    def get_open_activation_period(self, p_mitarbeiter_id: int):
        for period in reversed(self._periods.get(p_mitarbeiter_id, [])):
            if str(period.get("ende_datum", "")).strip() == "":
                return period
        return None

    def add_activation_period(self, p_mitarbeiter_id: int, p_start_datum: date, p_ende_datum=None):
        entries = self._periods.setdefault(p_mitarbeiter_id, [])
        entries.append(
            {
                "id": len(entries) + 1,
                "start_datum": p_start_datum.isoformat(),
                "ende_datum": p_ende_datum.isoformat() if p_ende_datum else "",
            }
        )

    def close_activation_period(self, p_period_id: int, p_ende_datum: date):
        for entries in self._periods.values():
            for period in entries:
                if int(period["id"]) == int(p_period_id):
                    period["ende_datum"] = p_ende_datum.isoformat()
                    return

    def set_current_activation_window(self, p_mitarbeiter_id: int, p_start_datum: date, p_ende_datum=None):
        analyst = self._analysts[p_mitarbeiter_id]
        analyst.start_datum = p_start_datum
        analyst.ende_datum = p_ende_datum


def test_activate_adds_open_period() -> None:
    repository = _FakeRepository()
    service = MitarbeiterAktivierungService(repository)

    service.activate(1, date(2026, 3, 1))

    periods = service.get_periods(1)
    assert len(periods) == 1
    assert periods[0]["start_datum"] == "2026-03-01"
    assert periods[0]["ende_datum"] == ""


def test_activate_raises_when_already_active() -> None:
    repository = _FakeRepository()
    repository.add_activation_period(1, date(2026, 1, 1), None)
    service = MitarbeiterAktivierungService(repository)

    with pytest.raises(DomainException, match="bereits aktiv"):
        service.activate(1, date(2026, 3, 1))


def test_deactivate_closes_open_period() -> None:
    repository = _FakeRepository()
    repository.add_activation_period(1, date(2026, 1, 1), None)
    service = MitarbeiterAktivierungService(repository)

    service.deactivate(1, date(2026, 3, 5))

    periods = service.get_periods(1)
    assert periods[0]["ende_datum"] == "2026-03-05"


def test_deactivate_raises_when_not_active() -> None:
    repository = _FakeRepository()
    service = MitarbeiterAktivierungService(repository)

    with pytest.raises(DomainException, match="nicht aktiv"):
        service.deactivate(1, date(2026, 3, 5))


def test_deactivate_validates_end_not_before_start() -> None:
    repository = _FakeRepository()
    repository.add_activation_period(1, date(2026, 3, 5), None)
    service = MitarbeiterAktivierungService(repository)

    with pytest.raises(DomainException, match="nicht vor Startdatum"):
        service.deactivate(1, date(2026, 3, 4))
