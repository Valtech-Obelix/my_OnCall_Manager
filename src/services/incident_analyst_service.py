# incident_analyst_service.py

from src.domain.incident_analyst import IncidentAnalyst


class IncidentAnalystService:

    def __init__(self, p_repository):
        self._repository = p_repository

    # Ref: UC-001
    def create(
        self,
        p_vornamen,
        p_nachname,
        p_email,
        p_start_datum,
        p_ende_datum=None
    ):

        analyst = IncidentAnalyst(
            p_id=None,
            p_vornamen=p_vornamen,
            p_nachname=p_nachname,
            p_email=p_email,
            p_start_datum=p_start_datum,
            p_ende_datum=p_ende_datum
        )

        return self._repository.add(analyst)

    # Ref: UC-002
    def delete(self, p_id: int):
        self._repository.delete(p_id)

    def get_all(self):
        return self._repository.get_all()