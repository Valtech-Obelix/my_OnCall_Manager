import  sys
import  logging
from    pathlib                                             import Path
from    PySide6.QtWidgets                                   import  QApplication
from    datetime                                            import  date
from    decimal                                             import  Decimal

from    src.ui.main_window                                  import  MainWindow
from    src.infrastructure.database                         import  Database
from    src.infrastructure.incident_analyst_repository      import  IncidentAnalystRepository
from    src.services.incident_analyst_service               import  IncidentAnalystService
from    src.infrastructure.logging_config                   import  setup_logging
from    src.domain.incident_analyst                         import  IncidentAnalyst
from    src.infrastructure.shift_repository                 import  ShiftRepository
from    src.services.opsgenie_service                       import  OpsGenieService
from    src.services.compensation_service                   import  CompensationService
from    src.infrastructure.opsgenie_client                  import  OpsGenieClient
from    src.infrastructure.oncall_location_repository       import  OnCallLocationRepository
from    src.infrastructure.gehaltsgruppe_repository         import  GehaltsgruppeRepository
from    src.infrastructure.secret_loader                    import  load_opsgenie_api_key
from    src.infrastructure.runtime_paths                    import  user_booking_data_dir
from    src.services.gehaltsgruppe_service                 import  GehaltsgruppeService
from    src.services.mitarbeiter_gehaltsgruppe_service     import  MitarbeiterGehaltsgruppeService
from    src.services.mitarbeiter_aktivierung_service       import  MitarbeiterAktivierungService

class Application:

    def __init__(self):
        setup_logging()
        self._logger = logging.getLogger(__name__)
        self._logger.info('')
        self._logger.info('=====================')
        self._logger.info(" Application started ")
        self._logger.info('=====================')
        self._logger.info('')

        api_key = load_opsgenie_api_key(self._logger.warning)
        self._opsgenie_client = None
        self._opsgenie_service = None
        if api_key:
            self._logger.info('OpsGenie API KEY geladen')
            self._opsgenie_client = OpsGenieClient(p_api_key=api_key)
        else:
            self._logger.warning(
                'Kein OpsGenie API-Key verfuegbar (ENV oder 1Password). '
                'OpsGenie-Import ist deaktiviert.'
            )

        self._qt_app = QApplication(sys.argv)

        self._database = Database()
        self._database.initialize_schema()

        self._analyst_repository = IncidentAnalystRepository(self._database.get_connection())
        self._incident_analyst_service = IncidentAnalystService(self._analyst_repository)
        self._oncall_location_repository = OnCallLocationRepository(
            self._database.get_connection()
        )
        self._gehaltsgruppe_repository = GehaltsgruppeRepository(
            self._database.get_connection()
        )
        self._gehaltsgruppe_service = GehaltsgruppeService(
            self._gehaltsgruppe_repository
        )
        self._mitarbeiter_gehaltsgruppe_service = MitarbeiterGehaltsgruppeService(
            self._analyst_repository,
            self._gehaltsgruppe_repository,
        )
        self._mitarbeiter_aktivierung_service = MitarbeiterAktivierungService(
            self._analyst_repository
        )

        # Ref: UC-004 – vollständige Verdrahtung
        self._shift_repository = ShiftRepository(self._database.get_connection())
        self._compensation_service = CompensationService()
        if self._opsgenie_client is not None:
            self._opsgenie_service = OpsGenieService    (  p_client=self._opsgenie_client
                                                         , p_shift_repository=self._shift_repository
                                                         , p_analyst_repository=self._analyst_repository
                                                         , p_logger=self._logger
                                                        )

        self._main_window = MainWindow(self)

    @property
    def opsgenie_service(self):
        return self._opsgenie_service


    def add_incident_analyst(
        self,
        p_vornamen: str,
        p_nachname: str,
        p_email: str,
        p_start_datum: date,
        p_ende_datum: date | None = None,
        p_oncall_location_id: str = "GER",
        p_mitarbeitertyp: str = "INCIDENT_ANALYST",
    ) -> IncidentAnalyst:

        return self._incident_analyst_service.create(
            p_vornamen,
            p_nachname,
            p_email,
            p_start_datum,
            p_ende_datum,
            p_oncall_location_id,
            p_mitarbeitertyp,
        )

    # Ref: UC-007 – Incident Analyst bearbeiten
    def update_incident_analyst(
        self,
        p_id: int,
        p_vornamen: str,
        p_nachname: str,
        p_email: str,
        p_start_datum: date,
        p_ende_datum: date | None = None,
        p_opsgenie_id: str | None = None,
        p_oncall_location_id: str = "GER",
        p_mitarbeitertyp: str = "INCIDENT_ANALYST",
    ) -> IncidentAnalyst:
        return self._incident_analyst_service.update(
            p_id=p_id,
            p_vornamen=p_vornamen,
            p_nachname=p_nachname,
            p_email=p_email,
            p_start_datum=p_start_datum,
            p_ende_datum=p_ende_datum,
            p_opsgenie_id=p_opsgenie_id,
            p_oncall_location_id=p_oncall_location_id,
            p_mitarbeitertyp=p_mitarbeitertyp,
        )

    def run(self):
        self._main_window.show()
        return self._qt_app.exec()

    # Ref: UC-002 v0.1 – Laden aller Incident Analysts
    def get_all_incident_analysts(self):
        return self._incident_analyst_service.get_all()

    # Ref: UC-002 v0.1 – Löschen eines Incident Analysts
    def delete_incident_analyst(self, p_id: int):
        self._incident_analyst_service.delete(p_id)

    # Ref: C-003: v.01 - Deaktiveren eines Incident Analysten
    def deactivate_incident_analyst(self, p_id: int, p_ende_datum):
        self._incident_analyst_service.deactivate(p_id, p_ende_datum)

    # Ref: UC-008 – Schichtplan anzeigen
    def get_schedule_references(self) -> list[dict[str, str]]:
        return self._shift_repository.get_schedule_references()

    # Ref: UC-008 – Schichtplan anzeigen
    def get_schedule_entries(self, p_schedule_id: str) -> list[dict[str, str | int | None]]:
        return self._shift_repository.get_schedule_entries(p_schedule_id)

    def get_booking_data_dir(self) -> Path:
        return user_booking_data_dir()

    # Ref: UC-009 – Aktive IA nach Schichtanzahl der letzten n Wochen
    def get_active_analyst_shift_counts_last_weeks(
        self,
        p_weeks: int
    ) -> list[dict[str, str | int]]:
        return self._shift_repository.get_active_analyst_shift_counts_last_weeks(p_weeks)

    def get_location_shift_distribution_last_weeks(
        self,
        p_weeks: int
    ) -> dict[str, list[dict[str, str | int | dict[str, int]]]]:
        return self._shift_repository.get_location_shift_distribution_last_weeks(p_weeks)

    def calculate_shift_compensation(
        self,
        p_oncall_location_id: str,
        p_start_time_utc: str,
    ) -> int:
        return self._compensation_service.calculate_shift_compensation(
            p_oncall_location_id=p_oncall_location_id,
            p_start_time_utc=p_start_time_utc,
        )

    def get_monthly_compensation_summary(
        self,
        p_year: int,
        p_month: int,
        p_location_filter: str | None = None,
    ) -> list[dict[str, str | int]]:
        analysts = self.get_all_incident_analysts()
        booking_entries = self._compensation_service.load_monthly_booking_entries(
            p_year=p_year,
            p_month=p_month,
        )
        overtime_entries = self._compensation_service.load_monthly_overtime_entries(
            p_year=p_year,
            p_month=p_month,
        )
        return self._compensation_service.summarize_monthly_compensation_from_bookings(
            p_booking_entries=booking_entries,
            p_overtime_entries=overtime_entries,
            p_analysts=analysts,
            p_location_filter=p_location_filter,
        )

    def get_monthly_compensation_details(
        self,
        p_year: int,
        p_month: int,
        p_analyst_id: int,
        p_location_filter: str | None = None,
    ) -> list[dict[str, str | int]]:
        analysts = self.get_all_incident_analysts()
        booking_entries = self._compensation_service.load_monthly_booking_entries(
            p_year=p_year,
            p_month=p_month,
        )
        overtime_entries = self._compensation_service.load_monthly_overtime_entries(
            p_year=p_year,
            p_month=p_month,
        )
        return self._compensation_service.build_booking_compensation_details(
            p_booking_entries=booking_entries,
            p_overtime_entries=overtime_entries,
            p_analysts=analysts,
            p_analyst_id=p_analyst_id,
            p_location_filter=p_location_filter,
        )

    # Ref: UC-020 – Client Utilized Kosten vorladen
    def get_client_utilized_costs_for_month(
        self,
        p_year: int,
        p_month: int,
        p_location_filter: str | None = None,
    ) -> list[dict[str, str]]:
        entries = self._compensation_service.load_monthly_client_utilized_entries(
            p_year,
            p_month,
        )
        analysts = self.get_all_incident_analysts()

        analysts_by_name = {
            self._compensation_service._normalize_person_name(str(analyst.buchungsname)): analyst
            for analyst in analysts
        }

        location_filter = p_location_filter.strip().upper() if p_location_filter else None
        rows: list[dict[str, str]] = []

        for entry in entries:
            analyst = analysts_by_name.get(
                self._compensation_service._normalize_person_name(str(entry["user"]))
            )
            if analyst is None:
                booking_date = date.fromisoformat(str(entry["booking_date"]))
                rows.append(
                    {
                        "booking_date": booking_date.strftime("%d.%m.%Y"),
                        "buchungsname": str(entry["user"]),
                        "task_name": str(entry["task_name"]),
                        "hours": self._compensation_service._format_hours(Decimal(str(entry["hours"]))),
                        "rate_eur": "0",
                        "cost_eur": "0",
                        "gehaltsgruppe": "",
                        "source_file": str(entry["source_file"]),
                        "status": "Mitarbeiter nicht gefunden",
                    }
                )
                continue

            location_id = str(analyst.oncall_location_id).strip().upper()
            if location_filter and location_id != location_filter:
                continue

            booking_date = date.fromisoformat(str(entry["booking_date"]))
            assignment = self._mitarbeiter_gehaltsgruppe_service.get_assignment_at(
                p_mitarbeiter_id=int(analyst.id),
                p_stichtag=booking_date,
            )
            if assignment is None:
                rows.append(
                    {
                        "booking_date": booking_date.strftime("%d.%m.%Y"),
                        "buchungsname": str(analyst.buchungsname),
                        "task_name": str(entry["task_name"]),
                        "hours": self._compensation_service._format_hours(Decimal(str(entry["hours"]))),
                        "rate_eur": "0",
                        "cost_eur": "0",
                        "gehaltsgruppe": "",
                        "group_amount": "",
                        "source_file": str(entry["source_file"]),
                        "status": "Keine Gehaltsgruppe am Buchungsdatum",
                    }
                )
                continue

            amount = self._gehaltsgruppe_service.get_betrag_am_stichtag(
                p_group_id=int(assignment["gehaltsgruppe_id"]),
                p_stichtag=booking_date,
            )
            if amount is None:
                betraege = self._gehaltsgruppe_service.get_betraege(
                    p_group_id=int(assignment["gehaltsgruppe_id"])
                )
                if len(betraege) == 0:
                    status_text = "Kein Betrag hinterlegt für diese Gehaltsgruppe"
                else:
                    status_text = "Kein Betrag mit gueltig_ab <= Buchungsdatum"
                    try:
                        future_dates = [
                            date.fromisoformat(str(item.get("gueltig_ab", "")))
                            for item in betraege
                        ]
                        future_dates = [d for d in future_dates if d > booking_date]
                        if future_dates:
                            status_text = (
                                "Kein Betrag für dieses Datum. "
                                f"Erster gültiger Betrag ab {min(future_dates).strftime('%d.%m.%Y')}"
                            )
                    except (TypeError, ValueError):
                        pass
                rows.append(
                    {
                        "booking_date": booking_date.strftime("%d.%m.%Y"),
                        "buchungsname": str(analyst.buchungsname),
                        "task_name": str(entry["task_name"]),
                        "hours": self._compensation_service._format_hours(Decimal(str(entry["hours"]))),
                        "rate_eur": "0",
                        "cost_eur": "0",
                        "gehaltsgruppe": str(assignment.get("gehaltsgruppe_bezeichnung", "")),
                        "group_amount": "",
                        "source_file": str(entry["source_file"]),
                        "status": status_text,
                    }
                )
                continue

            hours = Decimal(str(entry["hours"]))
            rate = Decimal(str(amount))
            cost = rate * hours
            rows.append(
                {
                    "booking_date": booking_date.strftime("%d.%m.%Y"),
                    "buchungsname": str(analyst.buchungsname),
                    "task_name": str(entry["task_name"]),
                    "hours": self._compensation_service._format_hours(hours),
                    "rate_eur": self._compensation_service._format_hours(rate),
                    "cost_eur": self._compensation_service._format_hours(cost),
                    "gehaltsgruppe": str(assignment.get("gehaltsgruppe_bezeichnung", "")),
                    "group_amount": self._compensation_service._format_hours(rate),
                    "source_file": str(entry["source_file"]),
                    "status": "",
                }
            )

        rows.sort(key=lambda row: (str(row.get("buchungsname", "")), str(row.get("booking_date", ""))))
        return rows

    # Ref: UC-009 – zuletzt verwendeten n-Wert persistieren
    def get_last_shift_count_weeks(self) -> int:
        value = self._shift_repository.get_setting("last_shift_count_weeks")
        if value is None:
            return 4
        try:
            parsed = int(value)
            return parsed if parsed > 0 else 4
        except ValueError:
            return 4

    # Ref: UC-009 – zuletzt verwendeten n-Wert persistieren
    def set_last_shift_count_weeks(self, p_weeks: int) -> None:
        self._shift_repository.set_setting("last_shift_count_weeks", str(int(p_weeks)))

    # Ref: UC-011 – Rufbereitschaftsstandorte
    def get_oncall_locations(self) -> list[dict[str, str]]:
        return self._oncall_location_repository.get_all()

    # Ref: UC-011 – Rufbereitschaftsstandorte
    def save_oncall_location(
        self,
        p_original_id: str | None,
        p_id: str,
        p_name: str
    ) -> None:
        if p_original_id:
            self._oncall_location_repository.update(
                p_original_id=p_original_id,
                p_new_id=p_id,
                p_name=p_name
            )
            return

        self._oncall_location_repository.add(p_id=p_id, p_name=p_name)

    # Ref: UC-011 – Rufbereitschaftsstandorte
    def oncall_location_exists(self, p_id: str) -> bool:
        return self._oncall_location_repository.exists(p_id)

    # Ref: UC-011 – Rufbereitschaftsstandorte
    def delete_oncall_location(self, p_id: str) -> None:
        self._oncall_location_repository.delete(p_id)

    # Ref: UC-017 – Gehaltsgruppen verwalten
    def create_gehaltsgruppe(
        self,
        p_bezeichnung: str,
        p_betrag: float,
        p_gueltig_ab: date,
        p_oncall_location_id: str = "GER",
    ):
        return self._gehaltsgruppe_service.create(
            p_bezeichnung=p_bezeichnung,
            p_betrag=p_betrag,
            p_gueltig_ab=p_gueltig_ab,
            p_oncall_location_id=p_oncall_location_id,
        )

    # Ref: UC-017 – Betragshistorie pflegen
    def update_gehaltsgruppe_betrag(
        self,
        p_group_id: int,
        p_betrag: float,
        p_gueltig_ab: date,
    ) -> None:
        self._gehaltsgruppe_service.update_betrag(
            p_group_id=p_group_id,
            p_betrag=p_betrag,
            p_gueltig_ab=p_gueltig_ab,
        )

    # Ref: UC-017 – Gehaltsgruppe aktualisieren
    def update_gehaltsgruppe_oncall_location(
        self,
        p_group_id: int,
        p_oncall_location_id: str,
    ) -> None:
        self._gehaltsgruppe_service.update_oncall_location(
            p_group_id=p_group_id,
            p_oncall_location_id=p_oncall_location_id,
        )

    # Ref: UC-017 – Stichtagsabfrage
    def get_gehaltsgruppe_betrag_am_stichtag(
        self,
        p_group_id: int,
        p_stichtag: date,
    ) -> float | None:
        return self._gehaltsgruppe_service.get_betrag_am_stichtag(
            p_group_id=p_group_id,
            p_stichtag=p_stichtag,
        )

    # Ref: UC-017 – Gehaltsgruppen anzeigen
    def get_gehaltsgruppen(self):
        return self._gehaltsgruppe_service.get_all()

    # Ref: UC-017 – Betragshistorie anzeigen
    def get_gehaltsgruppe_betraege(self, p_group_id: int):
        return self._gehaltsgruppe_service.get_betraege(p_group_id)

    # Ref: UC-019 – Gehaltsklassenzuordnung zu Mitarbeiter pflegen
    def assign_gehaltsgruppe_to_mitarbeiter(
        self,
        p_mitarbeiter_id: int,
        p_gehaltsgruppe_id: int,
        p_gueltig_ab: date,
        p_gueltig_bis: date | None = None,
    ) -> None:
        self._mitarbeiter_gehaltsgruppe_service.assign(
            p_mitarbeiter_id=p_mitarbeiter_id,
            p_gehaltsgruppe_id=p_gehaltsgruppe_id,
            p_gueltig_ab=p_gueltig_ab,
            p_gueltig_bis=p_gueltig_bis,
        )

    # Ref: UC-019 – Gehaltsklassenzuordnungen anzeigen
    def get_gehaltsgruppen_assignments_for_mitarbeiter(
        self,
        p_mitarbeiter_id: int
    ) -> list[dict[str, str | int]]:
        return self._mitarbeiter_gehaltsgruppe_service.get_assignments(p_mitarbeiter_id)

    # Ref: UC-019 – Gehaltsklasse am Stichtag
    def get_gehaltsgruppe_assignment_for_mitarbeiter_at(
        self,
        p_mitarbeiter_id: int,
        p_stichtag: date,
    ) -> dict[str, str | int] | None:
        return self._mitarbeiter_gehaltsgruppe_service.get_assignment_at(
            p_mitarbeiter_id=p_mitarbeiter_id,
            p_stichtag=p_stichtag,
        )

    # Ref: UC-019 v0.2 – Aktivierungsverlauf anzeigen
    def get_activation_periods_for_mitarbeiter(
        self,
        p_mitarbeiter_id: int,
    ) -> list[dict[str, str | int]]:
        return self._mitarbeiter_aktivierung_service.get_periods(p_mitarbeiter_id)

    # Ref: UC-019 v0.2 – Letzten Aktivierungsstatus anzeigen
    def get_current_activation_period_for_mitarbeiter(
        self,
        p_mitarbeiter_id: int,
    ) -> dict[str, str | int] | None:
        return self._mitarbeiter_aktivierung_service.get_current_period(p_mitarbeiter_id)

    # Ref: UC-019 v0.2 – Mitarbeiter aktivieren
    def activate_mitarbeiter(
        self,
        p_mitarbeiter_id: int,
        p_start_datum: date,
    ) -> None:
        self._mitarbeiter_aktivierung_service.activate(
            p_mitarbeiter_id=p_mitarbeiter_id,
            p_start_datum=p_start_datum,
        )

    # Ref: UC-019 v0.2 – Mitarbeiter deaktivieren
    def deactivate_mitarbeiter(
        self,
        p_mitarbeiter_id: int,
        p_ende_datum: date,
    ) -> None:
        self._mitarbeiter_aktivierung_service.deactivate(
            p_mitarbeiter_id=p_mitarbeiter_id,
            p_ende_datum=p_ende_datum,
        )
