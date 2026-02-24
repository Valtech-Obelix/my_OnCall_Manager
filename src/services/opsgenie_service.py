import   os
import   logging
from     datetime                                          import (  datetime
                                                                   , timezone
                                                                  )
from     typing                                            import List

from     src.domain.shift                                  import Shift
from     src.infrastructure.shift_repository               import ShiftRepository
from     src.infrastructure.opsgenie_client                import OpsGenieClient


class OpsGenieService:
    """
    Ref: UC-004 v0.1

    - Steuert Import von OpsGenie-Schichten
    - Berücksichtigt letzten Importzeitpunkt
    - Parst JSON in Domain-Objekte
    - Persistiert Shifts
    """

    SOURCE_PREFIX = "opsgenie"

    def __init__(
        self,
        p_shift_repository: ShiftRepository,
    ):
        self._repository = p_shift_repository

        api_key = os.getenv("OPSGENIE_API_KEY")
        self._client = OpsGenieClient(api_key)

        self._logger = logging.getLogger(__name__)

    # --------------------------------------------------
    # Öffentliche API
    # --------------------------------------------------

    def import_schedule(self, p_schedule_id: str) -> int:

        source_key = f"{self.SOURCE_PREFIX}:{p_schedule_id}"

        last_import = self._repository.get_last_import(source_key)

        self._logger.info("Starting OpsGenie import for %s", p_schedule_id)

        response_json = self._client.get_schedule_timeline(
            p_schedule_id=p_schedule_id,
            p_since=last_import
        )

        shifts = self._parse_shifts(
            p_schedule_id=p_schedule_id,
            p_json=response_json
        )

        if not shifts:
            self._logger.info("No new shifts found.")
            return 0

        self._repository.add_many(shifts)

        now_utc = datetime.now(timezone.utc)
        self._repository.set_last_import(source_key, now_utc)

        self._logger.info("Imported %d shifts.", len(shifts))

        return len(shifts)

    # --------------------------------------------------
    # JSON Parsing
    # --------------------------------------------------

    def _parse_shifts(self, p_schedule_id: str, p_json: dict) -> List[Shift]:

        shifts: List[Shift] = []

        try:
            rotations = (
                p_json["data"]
                ["finalTimeline"]
                ["rotations"]
            )
        except KeyError:
            self._logger.error("Unexpected OpsGenie response structure.")
            return shifts

        for rotation in rotations:

            entries = rotation.get("entries", [])

            for entry in entries:

                recipient = entry.get("recipient", {})
                analyst_name = recipient.get("name")

                start = entry.get("startDate")
                end = entry.get("endDate")

                if not analyst_name or not start or not end:
                    continue

                start_dt = self._parse_utc(start)
                end_dt = self._parse_utc(end)

                shift = Shift(
                    p_id=None,
                    p_project="unknown",  # später erweiterbar
                    p_schedule_id=p_schedule_id,
                    p_analyst_name=analyst_name,
                    p_start=start_dt,
                    p_end=end_dt
                )

                shifts.append(shift)

        return shifts

    # --------------------------------------------------
    # Hilfsfunktionen
    # --------------------------------------------------

    def _parse_utc(self, p_value: str) -> datetime:
        # Erwartet Format: 2026-02-01T00:00:00Z
        return datetime.fromisoformat(
            p_value.replace("Z", "+00:00")
        )