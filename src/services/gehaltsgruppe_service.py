import sqlite3
from datetime import date

from src.domain.exceptions import DomainException
from src.domain.gehaltsgruppe import Gehaltsgruppe, GehaltsgruppenBetrag


class GehaltsgruppeService:
    def __init__(self, p_repository):
        self._repository = p_repository

    def create(
        self,
        p_bezeichnung: str,
        p_betrag: float,
        p_gueltig_ab: date,
    ) -> Gehaltsgruppe:
        self._ensure_gueltig_ab(p_gueltig_ab)
        gehaltsgruppe = Gehaltsgruppe(
            p_id=None,
            p_bezeichnung=p_bezeichnung,
        )
        initial_betrag = GehaltsgruppenBetrag(
            p_gehaltsgruppe_id=0,
            p_betrag=p_betrag,
            p_gueltig_ab=p_gueltig_ab,
        )
        try:
            return self._repository.add_with_initial_betrag(
                p_gehaltsgruppe=gehaltsgruppe,
                p_betrag=initial_betrag,
            )
        except sqlite3.IntegrityError as exc:
            raise DomainException("Gehaltsgruppe existiert bereits.") from exc

    def update_betrag(
        self,
        p_group_id: int,
        p_betrag: float,
        p_gueltig_ab: date,
    ) -> None:
        if not self._repository.exists(int(p_group_id)):
            raise DomainException("Gehaltsgruppe nicht gefunden.")

        self._ensure_gueltig_ab(p_gueltig_ab)
        try:
            self._repository.add_betrag(
                GehaltsgruppenBetrag(
                    p_gehaltsgruppe_id=int(p_group_id),
                    p_betrag=p_betrag,
                    p_gueltig_ab=p_gueltig_ab,
                )
            )
        except sqlite3.IntegrityError as exc:
            raise DomainException(
                "Fuer dieses gueltig-ab-Datum existiert bereits ein Betrag."
            ) from exc

    def get_betrag_am_stichtag(self, p_group_id: int, p_stichtag: date) -> float | None:
        if not self._repository.exists(int(p_group_id)):
            raise DomainException("Gehaltsgruppe nicht gefunden.")
        return self._repository.get_betrag_am_stichtag(
            p_group_id=int(p_group_id),
            p_stichtag=p_stichtag,
        )

    def get_all(self) -> list[Gehaltsgruppe]:
        return self._repository.get_all()

    def get_betraege(self, p_group_id: int) -> list[dict[str, str | float]]:
        if not self._repository.exists(int(p_group_id)):
            raise DomainException("Gehaltsgruppe nicht gefunden.")
        return self._repository.get_betraege(int(p_group_id))

    def _ensure_gueltig_ab(self, p_gueltig_ab: date | None) -> None:
        if p_gueltig_ab is None:
            raise DomainException("Gueltig-ab-Datum ist erforderlich.")
