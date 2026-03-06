from    datetime                             import date, timedelta
import   sqlite3

from    src.domain.exceptions                import DomainException


class BudgetService:
    def __init__(self, p_budget_repository):
        self._repository = p_budget_repository

    # ---------------------------
    # Quellen
    # ---------------------------
    def create_source(self, p_name: str) -> int:
        name = (p_name or "").strip()
        if not name:
            raise DomainException("Der Quellenname ist erforderlich.")
        try:
            return self._repository.add_source(name)
        except sqlite3.IntegrityError as exc:
            raise DomainException("Eine Budgetquelle mit diesem Namen existiert bereits.") from exc

    def get_sources(self, p_include_inactive: bool = False) -> list[dict[str, str | int]]:
        return self._repository.get_sources(p_include_inactive=p_include_inactive)

    def get_source(self, p_source_id: int) -> dict[str, str | int]:
        source = self._repository.get_source(int(p_source_id))
        if source is None:
            raise DomainException("Budgetquelle nicht gefunden.")
        return source

    def rename_source(self, p_source_id: int, p_name: str) -> None:
        source_id = int(p_source_id)
        name = (p_name or "").strip()
        if not name:
            raise DomainException("Der Quellenname ist erforderlich.")
        self._ensure_source_exists(source_id)
        try:
            self._repository.update_source(source_id, name)
        except sqlite3.IntegrityError as exc:
            raise DomainException("Eine Budgetquelle mit diesem Namen existiert bereits.") from exc

    def set_source_active(self, p_source_id: int, p_is_active: bool) -> None:
        source_id = int(p_source_id)
        self._ensure_source_exists(source_id)
        self._repository.set_source_active(source_id, bool(p_is_active))

    def delete_source(self, p_source_id: int) -> None:
        source_id = int(p_source_id)
        self._ensure_source_exists(source_id)
        self._repository.delete_source(source_id)

    # ---------------------------
    # Budgetzeiträume
    # ---------------------------
    def create_period(
        self,
        p_budget_source_id: int,
        p_gueltig_ab: date,
        p_betrag_eur: float,
        p_gueltig_bis: date,
        p_note: str | None = None,
    ) -> int:
        source_id = int(p_budget_source_id)
        self._ensure_source_exists(source_id)
        self._ensure_date_order(p_gueltig_ab, p_gueltig_bis)

        if p_betrag_eur is None:
            raise DomainException("Der Betrag ist erforderlich.")
        if p_betrag_eur < 0:
            raise DomainException("Betrag darf nicht negativ sein.")
        try:
            return self._repository.add_period(
                p_budget_source_id=source_id,
                p_gueltig_ab=p_gueltig_ab.isoformat(),
                p_gueltig_bis=p_gueltig_bis.isoformat(),
                p_betrag_eur=float(p_betrag_eur),
                p_note=p_note,
            )
        except sqlite3.IntegrityError as exc:
            raise DomainException(
                "Ein Budgetzeitraum mit diesem Startdatum für diese Quelle ist bereits vorhanden."
            ) from exc

    def update_period(
        self,
        p_period_id: int,
        p_gueltig_ab: date,
        p_betrag_eur: float,
        p_gueltig_bis: date,
        p_note: str | None = None,
    ) -> None:
        period_id = int(p_period_id)
        self._ensure_period_exists(period_id)
        self._ensure_date_order(p_gueltig_ab, p_gueltig_bis)

        if p_betrag_eur is None:
            raise DomainException("Der Betrag ist erforderlich.")
        if p_betrag_eur < 0:
            raise DomainException("Betrag darf nicht negativ sein.")

        self._repository.update_period(
            p_period_id=period_id,
            p_gueltig_ab=p_gueltig_ab.isoformat(),
            p_gueltig_bis=p_gueltig_bis.isoformat(),
            p_betrag_eur=float(p_betrag_eur),
            p_note=p_note,
        )

    def delete_period(self, p_period_id: int) -> None:
        period_id = int(p_period_id)
        self._ensure_period_exists(period_id)
        self._repository.delete_period(period_id)

    def get_periods(self, p_budget_source_id: int | None = None) -> list[dict[str, str | int | float]]:
        if p_budget_source_id is None:
            raise DomainException("Bitte eine Budgetquelle angeben.")
        source_id = int(p_budget_source_id)
        self._ensure_source_exists(source_id)
        return self._repository.get_periods_for_source(source_id)

    # ---------------------------
    # Gesamte Budgetquellen
    # ---------------------------
    def get_active_periods(self) -> list[dict[str, str | int | float]]:
        return self._repository.get_active_periods()

    def get_active_budget_total(self) -> float:
        periods = self.get_active_periods()
        return sum(float(period["betrag_eur"]) for period in periods)

    # ---------------------------
    # Berechnungen
    # ---------------------------
    def get_budget_for_date(self, p_day: date) -> float:
        return self._repository.get_budget_amount_for_date(p_day.isoformat())

    def get_budget_timeline(
        self,
        p_from: date,
        p_to: date,
    ) -> list[dict[str, str | int | float]]:
        if p_from > p_to:
            raise DomainException("Startdatum darf nicht nach dem Enddatum liegen.")

        first_day = date(p_from.year, p_from.month, 1)
        last_day = p_to
        result: list[dict[str, str | int | float]] = []
        while first_day <= last_day:
            month_end = self._month_end(first_day)
            if month_end > p_to:
                month_end = p_to

            amount = 0.0
            periods = self._repository.get_active_periods_in_range(
                p_from=first_day.isoformat(),
                p_to=month_end.isoformat(),
            )

            for period in periods:
                period_start = date.fromisoformat(str(period.get("gueltig_ab")))
                period_end = date.fromisoformat(str(period.get("gueltig_bis")))
                duration_months = self._months_between_inclusive(
                    period_start,
                    period_end,
                )
                if duration_months <= 0:
                    continue
                amount += float(period.get("betrag_eur", 0.0)) / float(duration_months)

            result.append(
                {
                    "from_date": first_day.isoformat(),
                    "to_date": month_end.isoformat(),
                    "label": f"{first_day.year:04d}-{first_day.month:02d}",
                    "amount_eur": amount,
                }
            )

            next_month = first_day.replace(day=1) + timedelta(days=32)
            first_day = date(next_month.year, next_month.month, 1)

        return result

    # ---------------------------
    # Intern
    # ---------------------------
    def _ensure_source_exists(self, p_source_id: int) -> None:
        if not self._repository.exists_source(p_source_id):
            raise DomainException("Budgetquelle nicht gefunden.")

    def _ensure_period_exists(self, p_period_id: int) -> None:
        if self._repository.get_period(p_period_id) is None:
            raise DomainException("Budgetzeitraum nicht gefunden.")

    def _ensure_date_order(self, p_from: date, p_to: date) -> None:
        if p_to < p_from:
            raise DomainException("Enddatum darf nicht vor dem Startdatum liegen.")

    @staticmethod
    def _month_end(p_month_start: date) -> date:
        month_end = (p_month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        return month_end

    @staticmethod
    def _months_between_inclusive(p_start: date, p_end: date) -> int:
        return (p_end.year - p_start.year) * 12 + (p_end.month - p_start.month) + 1
