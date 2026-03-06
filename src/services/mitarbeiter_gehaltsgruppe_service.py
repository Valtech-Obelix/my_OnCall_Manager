from datetime import date, timedelta

from src.domain.exceptions import DomainException


class MitarbeiterGehaltsgruppeService:
    def __init__(self, p_analyst_repository, p_gehaltsgruppe_repository):
        self._analyst_repository = p_analyst_repository
        self._gehaltsgruppe_repository = p_gehaltsgruppe_repository

    def assign(
        self,
        p_mitarbeiter_id: int,
        p_gehaltsgruppe_id: int,
        p_gueltig_ab: date,
        p_gueltig_bis: date | None = None,
    ) -> None:
        mitarbeiter_id = int(p_mitarbeiter_id)
        gehaltsgruppe_id = int(p_gehaltsgruppe_id)

        if self._analyst_repository.find_by_id(mitarbeiter_id) is None:
            raise DomainException("Mitarbeiter nicht gefunden.")
        if not self._gehaltsgruppe_repository.exists(gehaltsgruppe_id):
            raise DomainException("Gehaltsklasse nicht gefunden.")
        if p_gueltig_bis is not None and p_gueltig_bis < p_gueltig_ab:
            raise DomainException("Gueltig-bis darf nicht vor Gueltig-ab liegen.")

        assignments = self._analyst_repository.get_gehaltsgruppen_zuordnungen(mitarbeiter_id)
        for assignment in assignments:
            existing_start = date.fromisoformat(str(assignment["gueltig_ab"]))
            existing_end_text = str(assignment.get("gueltig_bis", "")).strip()
            existing_end = date.fromisoformat(existing_end_text) if existing_end_text else None

            # Korrekturfall: gleicher Zeitraum, nur Wert ersetzen
            if existing_start == p_gueltig_ab and existing_end == p_gueltig_bis:
                continue

            # Wechselfall: offene alte Zuordnung endet am Tag vor dem neuen Start.
            if (
                existing_start < p_gueltig_ab
                and existing_end is None
                and self._ranges_overlap(p_gueltig_ab, p_gueltig_bis, existing_start, existing_end)
            ):
                self._analyst_repository.update_gehaltsgruppen_zuordnung_end_date(
                    p_assignment_id=int(assignment["id"]),
                    p_gueltig_bis=p_gueltig_ab - timedelta(days=1),
                )
                continue

            if self._ranges_overlap(p_gueltig_ab, p_gueltig_bis, existing_start, existing_end):
                raise DomainException(
                    "Der Gueltigkeitszeitraum ueberlappt mit einer bestehenden Gehaltsklassenzuordnung."
                )

        self._analyst_repository.upsert_gehaltsgruppen_zuordnung(
            p_mitarbeiter_id=mitarbeiter_id,
            p_gehaltsgruppe_id=gehaltsgruppe_id,
            p_gueltig_ab=p_gueltig_ab,
            p_gueltig_bis=p_gueltig_bis,
        )

    def get_assignments(self, p_mitarbeiter_id: int) -> list[dict[str, str | int]]:
        return self._analyst_repository.get_gehaltsgruppen_zuordnungen(int(p_mitarbeiter_id))

    def get_assignment_at(
        self,
        p_mitarbeiter_id: int,
        p_stichtag: date,
    ) -> dict[str, str | int] | None:
        return self._analyst_repository.get_gehaltsgruppe_zuordnung_am_stichtag(
            p_mitarbeiter_id=int(p_mitarbeiter_id),
            p_stichtag=p_stichtag,
        )

    def _ranges_overlap(
        self,
        p_a_start: date,
        p_a_end: date | None,
        p_b_start: date,
        p_b_end: date | None,
    ) -> bool:
        a_end = p_a_end if p_a_end is not None else date.max
        b_end = p_b_end if p_b_end is not None else date.max
        return p_a_start <= b_end and p_b_start <= a_end
