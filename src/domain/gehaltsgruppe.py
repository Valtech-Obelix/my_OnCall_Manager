from datetime import date

from src.domain.exceptions import DomainException


class Gehaltsgruppe:
    def __init__(self, p_id: int | None, p_bezeichnung: str, p_oncall_location_id: str = "GER"):
        self.id = p_id
        self.bezeichnung = p_bezeichnung.strip()
        self.oncall_location_id = p_oncall_location_id.strip().upper()
        self._validate()

    def _validate(self) -> None:
        if not self.bezeichnung:
            raise DomainException("Bezeichnung darf nicht leer sein.")
        if len(self.oncall_location_id) != 3:
            raise DomainException("Standortkennung muss 3 Zeichen haben.")


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
