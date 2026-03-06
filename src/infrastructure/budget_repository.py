import   sqlite3


TABLE_SOURCE = "budget_source"
TABLE_PERIOD = "budget_period"


class BudgetRepository:

    def __init__(self, p_connection: sqlite3.Connection):
        self._connection = p_connection

    # ---------------------------
    # Quellen
    # ---------------------------
    def add_source(self, p_name: str) -> int:
        name = p_name.strip()
        cursor = self._connection.cursor()
        cursor.execute(
            f"INSERT INTO {TABLE_SOURCE} (name) VALUES (?)",
            (name,),
        )
        self._connection.commit()
        return int(cursor.lastrowid)

    def exists_source(self, p_source_id: int) -> bool:
        cursor = self._connection.cursor()
        cursor.execute(
            f"SELECT 1 FROM {TABLE_SOURCE} WHERE id = ?",
            (int(p_source_id),),
        )
        return cursor.fetchone() is not None

    def get_source(self, p_source_id: int) -> dict[str, str | int] | None:
        cursor = self._connection.cursor()
        cursor.execute(
            f"""
            SELECT id, name, is_active
            FROM {TABLE_SOURCE}
            WHERE id = ?
            """,
            (int(p_source_id),),
        )
        row = cursor.fetchone()
        if row is None:
            return None

        return {
            "id": int(row[0]),
            "name": str(row[1]),
            "is_active": int(row[2]),
        }

    def get_sources(self, p_include_inactive: bool = False) -> list[dict[str, str | int]]:
        cursor = self._connection.cursor()
        query = f"""
            SELECT id, name, is_active
            FROM {TABLE_SOURCE}
            ORDER BY is_active DESC, name ASC
        """
        if not p_include_inactive:
            query = query.replace(
                "ORDER BY is_active DESC, name ASC",
                "WHERE is_active = 1 ORDER BY is_active DESC, name ASC",
            )
        cursor.execute(query)
        rows = cursor.fetchall()
        sources = []
        for row in rows:
            sources.append(
                {
                    "id": int(row[0]),
                    "name": str(row[1]),
                    "is_active": int(row[2]),
                }
            )
        return sources

    def update_source(self, p_source_id: int, p_name: str) -> None:
        cursor = self._connection.cursor()
        cursor.execute(
            f"UPDATE {TABLE_SOURCE} SET name = ? WHERE id = ?",
            (p_name.strip(), int(p_source_id)),
        )
        self._connection.commit()

    def set_source_active(self, p_source_id: int, p_is_active: bool) -> None:
        cursor = self._connection.cursor()
        cursor.execute(
            f"UPDATE {TABLE_SOURCE} SET is_active = ? WHERE id = ?",
            (1 if p_is_active else 0, int(p_source_id)),
        )
        self._connection.commit()

    def delete_source(self, p_source_id: int) -> None:
        cursor = self._connection.cursor()
        cursor.execute(f"DELETE FROM {TABLE_SOURCE} WHERE id = ?", (int(p_source_id),))
        self._connection.commit()

    # ---------------------------
    # Budgetzeiträume
    # ---------------------------
    def add_period(
        self,
        p_budget_source_id: int,
        p_gueltig_ab: str,
        p_gueltig_bis: str,
        p_betrag_eur: float,
        p_note: str | None = None,
    ) -> int:
        cursor = self._connection.cursor()
        cursor.execute(
            f"""
            INSERT INTO {TABLE_PERIOD}
            (budget_source_id, gueltig_ab, gueltig_bis, betrag_eur, note)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                int(p_budget_source_id),
                p_gueltig_ab,
                p_gueltig_bis,
                float(p_betrag_eur),
                p_note.strip() if isinstance(p_note, str) else None,
            ),
        )
        self._connection.commit()
        return int(cursor.lastrowid)

    def get_period(self, p_period_id: int) -> dict[str, str | int | float] | None:
        cursor = self._connection.cursor()
        cursor.execute(
            f"""
            SELECT
                bp.id,
                bp.budget_source_id,
                bp.gueltig_ab,
                bp.gueltig_bis,
                bp.betrag_eur,
                bp.note,
                bs.name AS budget_source_name
            FROM {TABLE_PERIOD} bp
            JOIN {TABLE_SOURCE} bs ON bs.id = bp.budget_source_id
            WHERE bp.id = ?
            """,
            (int(p_period_id),),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return {
            "id": int(row[0]),
            "budget_source_id": int(row[1]),
            "gueltig_ab": str(row[2]),
            "gueltig_bis": str(row[3]),
            "betrag_eur": float(row[4]),
            "note": str(row[5]) if row[5] is not None else "",
            "budget_source_name": str(row[6]),
        }

    def get_periods_for_source(self, p_budget_source_id: int) -> list[dict[str, str | int | float]]:
        cursor = self._connection.cursor()
        cursor.execute(
            f"""
            SELECT
                bp.id,
                bp.budget_source_id,
                bp.gueltig_ab,
                bp.gueltig_bis,
                bp.betrag_eur,
                bp.note,
                bs.name AS budget_source_name
            FROM {TABLE_PERIOD} bp
            JOIN {TABLE_SOURCE} bs ON bs.id = bp.budget_source_id
            WHERE bp.budget_source_id = ?
            ORDER BY bp.gueltig_ab ASC, bp.id ASC
            """,
            (int(p_budget_source_id),),
        )
        rows = []
        for row in cursor.fetchall():
            rows.append(
                {
                    "id": int(row[0]),
                    "budget_source_id": int(row[1]),
                    "gueltig_ab": str(row[2]),
                    "gueltig_bis": str(row[3]),
                    "betrag_eur": float(row[4]),
                    "note": str(row[5]) if row[5] is not None else "",
                    "budget_source_name": str(row[6]),
                }
            )
        return rows

    def update_period(
        self,
        p_period_id: int,
        p_gueltig_ab: str,
        p_gueltig_bis: str,
        p_betrag_eur: float,
        p_note: str | None = None,
    ) -> None:
        cursor = self._connection.cursor()
        cursor.execute(
            f"""
            UPDATE {TABLE_PERIOD}
            SET gueltig_ab = ?,
                gueltig_bis = ?,
                betrag_eur = ?,
                note = ?
            WHERE id = ?
            """,
            (
                p_gueltig_ab,
                p_gueltig_bis,
                float(p_betrag_eur),
                p_note.strip() if isinstance(p_note, str) else None,
                int(p_period_id),
            ),
        )
        self._connection.commit()

    def delete_period(self, p_period_id: int) -> None:
        cursor = self._connection.cursor()
        cursor.execute(f"DELETE FROM {TABLE_PERIOD} WHERE id = ?", (int(p_period_id),))
        self._connection.commit()

    # ---------------------------
    # Berechnungen
    # ---------------------------
    def get_budget_amount_for_date(self, p_date: str, p_only_active_sources: bool = True) -> float:
        cursor = self._connection.cursor()
        query = f"""
            SELECT COALESCE(SUM(bp.betrag_eur), 0)
            FROM {TABLE_PERIOD} bp
            JOIN {TABLE_SOURCE} bs
              ON bs.id = bp.budget_source_id
            WHERE bp.gueltig_ab <= ?
              AND bp.gueltig_bis >= ?
        """
        params = [p_date, p_date]
        if p_only_active_sources:
            query += " AND bs.is_active = 1"
        cursor.execute(query, params)
        row = cursor.fetchone()
        return float(row[0]) if row is not None else 0.0

    def get_budget_amount_for_date_range(
        self,
        p_from: str,
        p_to: str,
        p_only_active_sources: bool = True,
    ) -> float:
        cursor = self._connection.cursor()
        query = f"""
            SELECT COALESCE(SUM(bp.betrag_eur), 0)
            FROM {TABLE_PERIOD} bp
            JOIN {TABLE_SOURCE} bs
              ON bs.id = bp.budget_source_id
            WHERE bp.gueltig_ab <= ?
              AND bp.gueltig_bis >= ?
        """
        params = [p_to, p_from]
        if p_only_active_sources:
            query += " AND bs.is_active = 1"
        cursor.execute(query, params)
        row = cursor.fetchone()
        return float(row[0]) if row is not None else 0.0

    def get_active_periods_in_range(
        self,
        p_from: str,
        p_to: str,
    ) -> list[dict[str, str | int | float]]:
        cursor = self._connection.cursor()
        cursor.execute(
            f"""
            SELECT
                bp.id,
                bp.budget_source_id,
                bp.gueltig_ab,
                bp.gueltig_bis,
                bp.betrag_eur,
                bp.note,
                bs.name AS budget_source_name,
                bs.is_active
            FROM {TABLE_PERIOD} bp
            JOIN {TABLE_SOURCE} bs ON bs.id = bp.budget_source_id
            WHERE bs.is_active = 1
              AND bp.gueltig_ab <= ?
              AND bp.gueltig_bis >= ?
            ORDER BY bp.gueltig_ab ASC, bp.id ASC
            """,
            (p_to, p_from),
        )
        rows = []
        for row in cursor.fetchall():
            rows.append(
                {
                    "id": int(row[0]),
                    "budget_source_id": int(row[1]),
                    "gueltig_ab": str(row[2]),
                    "gueltig_bis": str(row[3]),
                    "betrag_eur": float(row[4]),
                    "note": str(row[5]) if row[5] is not None else "",
                    "budget_source_name": str(row[6]),
                    "is_active": int(row[7]),
                }
            )
        return rows
