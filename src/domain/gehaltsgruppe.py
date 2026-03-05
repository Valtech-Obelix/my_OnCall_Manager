from datetime import date

from src.domain.exceptions import DomainException


class Gehaltsgruppe:
    def __init__(self, p_id: int | None, p_bezeichnung: str):
        self.id = p_id
        self.bezeichnung = p_bezeichnung.strip()
        self._validate()

    def _validate(self) -> None:
        if not self.bezeichnung:
            raise DomainException("Bezeichnung darf nicht leer sein.")


class GehaltsgruppenBetrag:
    def __init__(self, p_gehaltsgruppe_id: int, p_betrag: float, p_gueltig_ab: date):
        self.gehaltsgruppe_id = int(p_gehaltsgruppe_id)
        self.betrag = float(p_betrag)
        self.gueltig_ab = p_gueltig_ab
        self._validate()

    def _validate(self) -> None:
        if self.gehaltsgruppe_id < 0:
            raise DomainException("Gehaltsgruppe ist ungueltig.")
        if self.betrag < 0:
            raise DomainException("Betrag darf nicht negativ sein.")
        if self.gueltig_ab is None:
            raise DomainException("Gueltig-ab-Datum ist erforderlich.")
