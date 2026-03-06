import  sys
import  logging
from    pathlib                                             import Path
from    PySide6.QtWidgets                                   import  QApplication
from    datetime                                            import  date, datetime, timedelta
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
from    src.infrastructure.budget_repository               import  BudgetRepository
from    src.infrastructure.secret_loader                    import  load_opsgenie_api_key
from    src.infrastructure.runtime_paths                    import  user_booking_data_dir
from    src.services.gehaltsgruppe_service                 import  GehaltsgruppeService
from    src.services.mitarbeiter_gehaltsgruppe_service     import  MitarbeiterGehaltsgruppeService
from    src.services.mitarbeiter_aktivierung_service       import  MitarbeiterAktivierungService
from    src.services.budget_service                        import  BudgetService

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
        self._budget_repository = BudgetRepository(self._database.get_connection())
        self._budget_service = BudgetService(self._budget_repository)

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

    def get_overtime_costs_for_month(
        self,
        p_year: int,
        p_month: int,
        p_location_filter: str | None = None,
    ) -> list[dict[str, str]]:
        entries = self._compensation_service.load_monthly_overtime_entries(
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
                        "group_amount": "",
                        "source_file": str(entry["source_file"]),
                        "status": "Mitarbeiter nicht gefunden",
                    }
                )
                continue

            location_id = str(analyst.oncall_location_id).strip().upper()
            if location_filter and location_id != location_filter:
                continue

            booking_date = date.fromisoformat(str(entry["booking_date"]))
            bucket = self._compensation_service._overtime_bucket_for_task(
                p_task_name=str(entry["task_name"])
            )
            hours = Decimal(str(entry["hours"]))
            booking_count = int(entry.get("booking_count", 0))

            if bucket in ("GER_25", "GER_50"):
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
                            "hours": self._compensation_service._format_hours(hours),
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
                    rows.append(
                        {
                            "booking_date": booking_date.strftime("%d.%m.%Y"),
                            "buchungsname": str(analyst.buchungsname),
                            "task_name": str(entry["task_name"]),
                            "hours": self._compensation_service._format_hours(hours),
                            "rate_eur": "0",
                            "cost_eur": "0",
                            "gehaltsgruppe": str(assignment.get("gehaltsgruppe_bezeichnung", "")),
                            "group_amount": "",
                            "source_file": str(entry["source_file"]),
                            "status": "Kein Betrag für diesen Tag",
                        }
                    )
                    continue

                rate = Decimal(str(amount))
                multiplier = Decimal("1.25") if bucket == "GER_25" else Decimal("1.5")
                cost = hours * rate * multiplier
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
                        "status": f"Faktor {multiplier}",
                    }
                )
                continue

            if bucket in ("IND_MO_SA", "IND_SO"):
                cost = Decimal("10") * Decimal(booking_count)
                rows.append(
                    {
                        "booking_date": booking_date.strftime("%d.%m.%Y"),
                        "buchungsname": str(analyst.buchungsname),
                        "task_name": str(entry["task_name"]),
                        "hours": self._compensation_service._format_hours(hours),
                        "rate_eur": "10",
                        "cost_eur": self._compensation_service._format_hours(cost),
                        "gehaltsgruppe": "",
                        "group_amount": "",
                        "source_file": str(entry["source_file"]),
                        "status": "",
                    }
                )
                continue

            rows.append(
                {
                    "booking_date": booking_date.strftime("%d.%m.%Y"),
                    "buchungsname": str(analyst.buchungsname),
                    "task_name": str(entry["task_name"]),
                    "hours": self._compensation_service._format_hours(hours),
                    "rate_eur": "0",
                    "cost_eur": "0",
                    "gehaltsgruppe": "",
                    "group_amount": "",
                    "source_file": str(entry["source_file"]),
                    "status": "Unbekannter Overtime Task",
                }
            )

        rows.sort(key=lambda row: (str(row.get("buchungsname", "")), str(row.get("booking_date", ""))))
        return rows

    def get_on_call_costs_for_month(
        self,
        p_year: int,
        p_month: int,
        p_location_filter: str | None = None,
    ) -> list[dict[str, str]]:
        entries = self._compensation_service.load_monthly_booking_entries(
            p_year=p_year,
            p_month=p_month,
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
                        "slot": str(entry["slot"]),
                        "hours": "1",
                        "rate_eur": "0",
                        "cost_eur": "0",
                        "source_file": str(entry["source_file"]),
                        "status": "Mitarbeiter nicht gefunden",
                    }
                )
                continue

            location_id = str(analyst.oncall_location_id).strip().upper()
            if location_filter and location_id != location_filter:
                continue

            booking_date = date.fromisoformat(str(entry["booking_date"]))
            slot = str(entry["slot"])
            try:
                base_rate = Decimal(str(self._compensation_service._calculate_amount_for_day_slot(
                    p_oncall_location_id=location_id,
                    p_day=booking_date,
                    p_slot=slot,
                )))
            except Exception:
                rows.append(
                    {
                        "booking_date": booking_date.strftime("%d.%m.%Y"),
                        "buchungsname": str(analyst.buchungsname),
                        "task_name": str(entry["task_name"]),
                        "slot": slot,
                        "hours": "1",
                        "group_amount": "0",
                        "rate_eur": "0",
                        "lnk_eur": "0",
                        "cost_eur": "0",
                        "source_file": str(entry["source_file"]),
                        "status": "Ungültiger Buchungseintrag",
                    }
                )
                continue

            if location_id == "GER":
                lnk_amount = base_rate * Decimal("0.25")
                shift_base = base_rate
                gehaltsgruppe_amount = Decimal("0")
            else:
                gehaltsgruppe_amount = Decimal("0")
                assignment = self._mitarbeiter_gehaltsgruppe_service.get_assignment_at(
                    p_mitarbeiter_id=int(analyst.id),
                    p_stichtag=booking_date,
                )
                if assignment is not None:
                    amount = self._gehaltsgruppe_service.get_betrag_am_stichtag(
                        p_group_id=int(assignment["gehaltsgruppe_id"]),
                        p_stichtag=booking_date,
                    )
                    if amount is not None:
                        gehaltsgruppe_amount = Decimal(str(amount))

                day_type = self._compensation_service.determine_day_type(booking_date)
                is_weekend = day_type in ("SATURDAY", "SUNDAY_OR_HOLIDAY")
                lnk_amount = gehaltsgruppe_amount * Decimal("4") if is_weekend else Decimal("0")
                shift_base = Decimal("6")
                gehaltsgruppe_amount = gehaltsgruppe_amount

            rows.append(
                {
                    "booking_date": booking_date.strftime("%d.%m.%Y"),
                    "buchungsname": str(analyst.buchungsname),
                    "task_name": str(entry["task_name"]),
                    "slot": slot,
                    "hours": "1",
                    "group_amount": self._compensation_service._format_hours(gehaltsgruppe_amount),
                    "rate_eur": self._compensation_service._format_hours(shift_base),
                    "lnk_eur": self._compensation_service._format_hours(lnk_amount),
                    "cost_eur": self._compensation_service._format_hours(shift_base + lnk_amount),
                    "source_file": str(entry["source_file"]),
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

    # Ref: UC-021 – Budgetquellen verwalten
    def create_budget_source(self, p_name: str) -> int:
        return self._budget_service.create_source(p_name=p_name)

    # Ref: UC-021 – Budgetquellen anzeigen
    def get_budget_sources(self, p_include_inactive: bool = False) -> list[dict[str, str | int]]:
        return self._budget_service.get_sources(p_include_inactive=p_include_inactive)

    # Ref: UC-021 – Budgetquelle abrufen
    def get_budget_source(self, p_source_id: int) -> dict[str, str | int]:
        return self._budget_service.get_source(p_source_id=p_source_id)

    # Ref: UC-021 – Budgetquelle umbenennen
    def rename_budget_source(self, p_source_id: int, p_name: str) -> None:
        self._budget_service.rename_source(p_source_id=p_source_id, p_name=p_name)

    # Ref: UC-021 – Budgetquelle aktiv/inaktiv setzen
    def set_budget_source_active(self, p_source_id: int, p_is_active: bool) -> None:
        self._budget_service.set_source_active(
            p_source_id=p_source_id,
            p_is_active=p_is_active,
        )

    # Ref: UC-021 – Budgetquelle löschen
    def delete_budget_source(self, p_source_id: int) -> None:
        self._budget_service.delete_source(p_source_id=p_source_id)

    # Ref: UC-021 – Budgetzeitraum anlegen
    def create_budget_period(
        self,
        p_budget_source_id: int,
        p_gueltig_ab: date,
        p_betrag_eur: float,
        p_gueltig_bis: date,
        p_note: str | None = None,
    ) -> int:
        return self._budget_service.create_period(
            p_budget_source_id=p_budget_source_id,
            p_gueltig_ab=p_gueltig_ab,
            p_gueltig_bis=p_gueltig_bis,
            p_betrag_eur=p_betrag_eur,
            p_note=p_note,
        )

    # Ref: UC-021 – Budgetzeiträume abrufen
    def get_budget_periods(
        self,
        p_budget_source_id: int,
    ) -> list[dict[str, str | int | float]]:
        return self._budget_service.get_periods(p_budget_source_id=p_budget_source_id)

    # Ref: UC-021 – Budgetzeitraum bearbeiten
    def update_budget_period(
        self,
        p_period_id: int,
        p_gueltig_ab: date,
        p_betrag_eur: float,
        p_gueltig_bis: date,
        p_note: str | None = None,
    ) -> None:
        self._budget_service.update_period(
            p_period_id=p_period_id,
            p_gueltig_ab=p_gueltig_ab,
            p_gueltig_bis=p_gueltig_bis,
            p_betrag_eur=p_betrag_eur,
            p_note=p_note,
        )

    # Ref: UC-021 – Budgetzeitraum entfernen
    def delete_budget_period(self, p_period_id: int) -> None:
        self._budget_service.delete_period(p_period_id=p_period_id)

    # Ref: UC-021 – Budget am Tag
    def get_budget_for_date(self, p_day: date) -> float:
        return self._budget_service.get_budget_for_date(p_day=p_day)

    # Ref: UC-021 – Budgetzeitachse anzeigen
    def get_budget_timeline(
        self,
        p_from: date,
        p_to: date,
    ) -> list[dict[str, str | int | float]]:
        return self._budget_service.get_budget_timeline(
            p_from=p_from,
            p_to=p_to,
        )

    # Ref: UC-021 – Budgetdaten für Burndown
    def get_budget_active_periods(self) -> list[dict[str, str | int | float]]:
        return self._budget_service.get_active_periods()

    # Ref: UC-021 – Budgetgesamtwert
    def get_total_active_budget(self) -> float:
        return self._budget_service.get_active_budget_total()

    # Ref: UC-022 – Burndown-Konfiguration
    def get_burndown_forecast_weeks(self) -> int:
        value = self._shift_repository.get_setting("budget_burndown_forecast_weeks")
        if value is None:
            return 4
        try:
            parsed = int(value)
            return parsed if parsed > 0 else 4
        except ValueError:
            return 4

    # Ref: UC-022 – Burndown-Konfiguration
    def set_burndown_forecast_weeks(self, p_weeks: int) -> None:
        self._shift_repository.set_setting("budget_burndown_forecast_weeks", str(int(p_weeks)))

    # Ref: UC-022 – Burndown-Daten
    def get_budget_burndown_data(self, p_forecast_weeks: int) -> dict[str, object]:
        periods = self.get_budget_active_periods()
        if len(periods) == 0:
            raise DomainException("Es ist kein aktives Budget vorhanden.")

        week_count_total = sum(float(period.get("betrag_eur", 0.0)) for period in periods)
        if week_count_total <= 0:
            raise DomainException("Das Gesamtbudget ist 0. Bitte Budgets korrigieren.")

        start_date = min(date.fromisoformat(str(period["gueltig_ab"])) for period in periods)
        end_date = max(date.fromisoformat(str(period["gueltig_bis"])) for period in periods)
        week_buckets = self._build_week_buckets(start_date=start_date, p_end=end_date)
        week_index_by_start = {
            bucket_start: idx for idx, (bucket_start, _bucket_end) in enumerate(week_buckets)
        }

        plan_values = self._build_plan_series(
            p_week_buckets=week_buckets,
            p_periods=periods,
        )

        today = date.today()
        current_monday = today - timedelta(days=today.weekday())
        actual_end = current_monday - timedelta(days=1)
        if actual_end > end_date:
            actual_end = end_date

        actual_week_values = self._build_actual_weekly_costs(
            p_week_index_by_start=week_index_by_start,
            p_from=start_date,
            p_to=min(end_date, actual_end),
        )

        actual_cumulative: list[float] = []
        total_actual = Decimal("0")
        actual_last_index = -1
        for idx in range(len(week_buckets)):
            if self._week_is_within_actual_window(week_buckets[idx][1], actual_end):
                total_actual += Decimal(str(actual_week_values[idx]))
                actual_last_index = idx
            actual_cumulative.append(float(total_actual))

        if actual_last_index < 0:
            forecast_values: list[tuple[int, float]] = []
        else:
            forecast_values = self._build_forecast_series(
                p_actual_week_values=actual_week_values,
                p_actual_cumulative=actual_cumulative,
                p_last_actual_index=actual_last_index,
                p_weeks_back=max(1, int(p_forecast_weeks)),
            )

        labels = [(start + timedelta(days=6)).isoformat() for start, _end in week_buckets]
        payload: dict[str, object] = {
            "labels": labels,
            "plan": plan_values,
            "total_budget": float(week_count_total),
            "actual": [
                {"week_index": int(index), "value": float(value)}
                for index, value in enumerate(actual_cumulative[: actual_last_index + 1])
            ] if actual_last_index >= 0 else [],
            "forecast": [
                {"week_index": int(index), "value": float(value)}
                for index, value in forecast_values
            ],
        }
        return payload

    def _build_week_buckets(self, start_date: date, p_end: date) -> list[tuple[date, date]]:
        buckets = []
        if p_end < start_date:
            return buckets

        current_start = start_date - timedelta(days=start_date.weekday())
        while current_start <= p_end:
            bucket_end = current_start + timedelta(days=6)
            if bucket_end > p_end:
                bucket_end = p_end
            buckets.append((current_start, bucket_end))
            current_start += timedelta(weeks=1)
        return buckets

    def _build_plan_series(
        self,
        p_week_buckets: list[tuple[date, date]],
        p_periods: list[dict[str, str | int | float]],
    ) -> list[float]:
        cumulative = Decimal("0")
        plan_values: list[float] = []
        parsed_periods = []
        for period in p_periods:
            period_start = date.fromisoformat(str(period["gueltig_ab"]))
            period_end = date.fromisoformat(str(period["gueltig_bis"]))
            period_months = self._months_between_inclusive(period_start, period_end)
            if period_months <= 0:
                continue
            parsed_periods.append(
                (
                    period_start,
                    period_end,
                    Decimal(str(period["betrag_eur"])),
                    period_months,
                )
            )

        for bucket_start, bucket_end in p_week_buckets:
            weekly_amount = Decimal("0")
            for period_start, period_end, amount, period_months in parsed_periods:
                if period_end < bucket_start or period_start > bucket_end:
                    continue

                monthly_amount = amount / Decimal(period_months)
                for year, month in self._iterate_months(period_start, period_end):
                    month_start = date(year, month, 1)
                    month_end = self._month_end(month_start)
                    overlap_start = max(bucket_start, month_start, period_start)
                    overlap_end = min(bucket_end, month_end, period_end)
                    if overlap_start > overlap_end:
                        continue
                    overlap_days = Decimal((overlap_end - overlap_start).days + 1)
                    month_days = Decimal((month_end - month_start).days + 1)
                    if month_days <= 0:
                        continue
                    weekly_amount += monthly_amount * overlap_days / month_days

                continue
            cumulative += weekly_amount
            plan_values.append(float(cumulative))

        return plan_values

    def _build_actual_weekly_costs(
        self,
        p_week_index_by_start: dict[date, int],
        p_from: date,
        p_to: date,
    ) -> list[float]:
        values = [0.0] * len(p_week_index_by_start)
        if p_to < p_from:
            return values

        def _to_decimal(p_raw: object) -> Decimal:
            if p_raw is None:
                return Decimal("0")
            try:
                return Decimal(str(p_raw).replace(",", "."))
            except Exception:
                return Decimal("0")

        def _add_month_costs(p_rows: list[dict[str, str]]) -> None:
            for row in p_rows:
                booking_date = row.get("booking_date")
                if booking_date is None:
                    continue
                try:
                    parsed_date = date.fromisoformat(str(booking_date))
                except ValueError:
                    try:
                        parsed_date = datetime.strptime(str(booking_date), "%d.%m.%Y").date()
                    except Exception:
                        continue
                if parsed_date < p_from or parsed_date > p_to:
                    continue
                week_start = parsed_date - timedelta(days=parsed_date.weekday())
                week_index = p_week_index_by_start.get(week_start)
                if week_index is None:
                    continue
                amount = _to_decimal(row.get("cost_eur"))
                values[week_index] += float(amount)

        for year, month in self._iterate_months(p_from, p_to):
            client_entries = self.get_client_utilized_costs_for_month(
                p_year=year,
                p_month=month,
            )
            overtime_entries = self.get_overtime_costs_for_month(
                p_year=year,
                p_month=month,
            )
            oncall_entries = self.get_on_call_costs_for_month(
                p_year=year,
                p_month=month,
            )
            _add_month_costs(client_entries)
            _add_month_costs(overtime_entries)
            _add_month_costs(oncall_entries)
        return values

    def _build_forecast_series(
        self,
        p_actual_week_values: list[float],
        p_actual_cumulative: list[float],
        p_last_actual_index: int,
        p_weeks_back: int,
    ) -> list[tuple[int, float]]:
        if p_last_actual_index < 0:
            return []

        start = max(0, p_last_actual_index - p_weeks_back + 1)
        window = p_actual_week_values[start : p_last_actual_index + 1]
        if len(window) == 0:
            return []

        total = Decimal("0")
        for value in window:
            total += Decimal(str(value))
        average = total / Decimal(len(window))

        forecast: list[tuple[int, float]] = []
        running = Decimal(str(p_actual_cumulative[p_last_actual_index]))
        last_idx = len(p_actual_week_values) - 1
        forecast.append((p_last_actual_index, float(running)))
        for idx in range(p_last_actual_index + 1, last_idx + 1):
            running += average
            forecast.append((idx, float(running)))
        return forecast

    @staticmethod
    def _month_end(p_month_start: date) -> date:
        return (p_month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

    @staticmethod
    def _months_between_inclusive(p_start: date, p_end: date) -> int:
        return (p_end.year - p_start.year) * 12 + (p_end.month - p_start.month) + 1

    def _iterate_months(self, p_from: date, p_to: date) -> list[tuple[int, int]]:
        if p_to < p_from:
            return []
        months = []
        current_year = p_from.year
        current_month = p_from.month
        while (current_year, current_month) <= (p_to.year, p_to.month):
            months.append((current_year, current_month))
            if current_month == 12:
                current_year += 1
                current_month = 1
            else:
                current_month += 1
        return months

    @staticmethod
    def _week_is_within_actual_window(p_bucket_end: date, p_reference: date) -> bool:
        return p_bucket_end <= p_reference

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
