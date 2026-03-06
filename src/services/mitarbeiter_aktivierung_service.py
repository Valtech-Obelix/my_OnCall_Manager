from datetime import date

from src.domain.exceptions import DomainException


class MitarbeiterAktivierungService:
    def __init__(self, p_analyst_repository):
        self._analyst_repository = p_analyst_repository

    def get_periods(self, p_mitarbeiter_id: int) -> list[dict[str, str | int]]:
        self._ensure_mitarbeiter_exists(p_mitarbeiter_id)
        return self._analyst_repository.get_activation_periods(int(p_mitarbeiter_id))

    def get_current_period(self, p_mitarbeiter_id: int) -> dict[str, str | int] | None:
        self._ensure_mitarbeiter_exists(p_mitarbeiter_id)
        open_period = self._analyst_repository.get_open_activation_period(int(p_mitarbeiter_id))
        if open_period is not None:
            return open_period

        periods = self._analyst_repository.get_activation_periods(int(p_mitarbeiter_id))
        if not periods:
            return None
        return periods[-1]

    def activate(self, p_mitarbeiter_id: int, p_start_datum: date) -> None:
        mitarbeiter_id = int(p_mitarbeiter_id)
        self._ensure_mitarbeiter_exists(mitarbeiter_id)

        open_period = self._analyst_repository.get_open_activation_period(mitarbeiter_id)
        if open_period is not None:
            raise DomainException("Mitarbeiter ist bereits aktiv.")

        self._analyst_repository.add_activation_period(
            p_mitarbeiter_id=mitarbeiter_id,
            p_start_datum=p_start_datum,
            p_ende_datum=None,
        )
        self._analyst_repository.set_current_activation_window(
            p_mitarbeiter_id=mitarbeiter_id,
            p_start_datum=p_start_datum,
            p_ende_datum=None,
        )

    def deactivate(self, p_mitarbeiter_id: int, p_ende_datum: date) -> None:
        mitarbeiter_id = int(p_mitarbeiter_id)
        self._ensure_mitarbeiter_exists(mitarbeiter_id)

        open_period = self._analyst_repository.get_open_activation_period(mitarbeiter_id)
        if open_period is None:
            raise DomainException("Mitarbeiter ist nicht aktiv.")

        start_datum = date.fromisoformat(str(open_period["start_datum"]))
        if p_ende_datum < start_datum:
            raise DomainException("Enddatum darf nicht vor Startdatum liegen.")

        self._analyst_repository.close_activation_period(
            p_period_id=int(open_period["id"]),
            p_ende_datum=p_ende_datum,
        )
        self._analyst_repository.set_current_activation_window(
            p_mitarbeiter_id=mitarbeiter_id,
            p_start_datum=start_datum,
            p_ende_datum=p_ende_datum,
        )

    def _ensure_mitarbeiter_exists(self, p_mitarbeiter_id: int) -> None:
        if self._analyst_repository.find_by_id(int(p_mitarbeiter_id)) is None:
            raise DomainException("Mitarbeiter nicht gefunden.")
