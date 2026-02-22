# incident_analyst_service.py
import   logging
from     datetime                                          import date
from     src.domain.incident_analyst                       import IncidentAnalyst
from     src.domain.exceptions                             import DomainException

class IncidentAnalystService:

    def __init__(self, p_repository):
        self._logger = logging.getLogger(__name__)
        self._repository = p_repository

    # Ref: UC-001
    def create(  self
               , p_vornamen
               , p_nachname
               , p_email
               , p_start_datum
               , p_ende_datum=None
              ):
        self._logger.debug(  "Input data: %s %s %s %s %s"
                           , p_vornamen
                           , p_nachname
                           , p_email
                           , p_start_datum
                           , p_ende_datum
                        )
                                
        try:
            analyst = IncidentAnalyst(  p_id      = None
                                  , p_vornamen    = p_vornamen
                                  , p_nachname    = p_nachname
                                  , p_email       = p_email
                                  , p_start_datum = p_start_datum
                                  , p_ende_datum  = p_ende_datum
                                 )
            result  = self._repository.add(analyst)
            self._logger.info(  "Creating IncidentAnalyst: %s, %s"
                              , p_nachname
                              , p_vornamen
                             )
        except Exception as e:
            self._logger.error("Error while creating IncidentAnalyst: %s", str(e), exc_info=True)
            raise

    # Ref: UC-002
    def delete(self, p_id: int):
        self._logger.debug("Deleting IncidentAnalyst with id=%s", p_id)

        try:
            self._repository.delete(p_id)

            self._logger.info("Deleting IncidentAnalyst with id=%s", p_id)
            self._logger.debug("Delete operation executed")
        except Exception as e:
            self._logger.error("Error while deleting IncidentAnalyst: %s", str(e), exc_info=True)
            raise

    # Ref: UC-003
    def deactivate(self, p_id: int, p_ende_datum: date):

        analysts = self._repository.get_all()
        analyst = next((a for a in analysts if a.id == p_id), None)

        if analyst is None:
            raise DomainException("IncidentAnalyst nicht gefunden.")

        if not analyst.is_active:
            raise DomainException("IncidentAnalyst ist bereits deaktiviert.")

        if p_ende_datum < analyst.start_datum:
            raise DomainException("Enddatum darf nicht vor Startdatum liegen.")

        self._logger.info("Deactivating IncidentAnalyst id=%s", p_id)

        self._repository.update_end_date(p_id, p_ende_datum)

    def get_all(self):
        return self._repository.get_all()