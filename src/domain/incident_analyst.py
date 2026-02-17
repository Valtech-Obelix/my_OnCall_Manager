# incident_analyst.py

import   re
from     datetime                                 import date


class IncidentAnalyst:
    """
    Domain Entity: IncidentAnalyst

    Ref: UC-001 v0.2
    - Erweiterung um Vorname/Nachname
    - Einführung Gültigkeitszeitraum
    - Buchungsname als abgeleitetes Attribut

    Ref: UC-001 v0.1
    - Basic version mit Name und Email
    """

    def __init__(
        self,
        p_vorname: str,
        p_nachname: str,
        p_email: str,
        p_start_datum: date,
        p_end_datum: date | None = None
    ):
        # Ref: UC-001 v0.2 – neue Attribute
        self.vorname = p_vorname.strip()
        self.nachname = p_nachname.strip()
        self.email = p_email.strip()
        self.start_datum = p_start_datum
        self.end_datum = p_end_datum

        self._validate()

    # Ref: UC-001 v0.2 – Buchungsname abgeleitet
    @property
    def buchungsname(self) -> str:
        return f'{self.nachname}, {self.vorname}'

    # Ref: UC-001 v0.2 – Erweiterte Validierung
    def _validate(self) -> None:

        if not self.vorname:
            raise ValueError('Vorname darf nicht leer sein.')

        if not self.nachname:
            raise ValueError('Nachname darf nicht leer sein.')

        if not self._is_valid_email():
            raise ValueError('Ungültiges Email-Format.')

        if self.end_datum and self.end_datum < self.start_datum:
            raise ValueError('Enddatum darf nicht vor Startdatum liegen.')

    def _is_valid_email(self) -> bool:
        pattern = r'^[^@]+@[^@]+\.[^@]+$'
        return re.match(pattern, self.email) is not None
