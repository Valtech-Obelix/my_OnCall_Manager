import sqlite3
from datetime import date

from src.domain.gehaltsgruppe import Gehaltsgruppe, GehaltsgruppenBetrag


class GehaltsgruppeRepository:
    def __init__(self, p_connection: sqlite3.Connection):
        self._connection = p_connection

    def add(self, p_gehaltsgruppe: Gehaltsgruppe) -> Gehaltsgruppe:
        cursor = self._connection.cursor()
        cursor.execute(
            """
            INSERT INTO gehaltsgruppe (bezeichnung)
            VALUES (?)
            """,
            (p_gehaltsgruppe.bezeichnung,),
        )
        self._connection.commit()
        return Gehaltsgruppe(p_id=cursor.lastrowid, p_bezeichnung=p_gehaltsgruppe.bezeichnung)

    def add_with_initial_betrag(
        self,
        p_gehaltsgruppe: Gehaltsgruppe,
        p_betrag: GehaltsgruppenBetrag,
    ) -> Gehaltsgruppe:
        cursor = self._connection.cursor()
        try:
            cursor.execute("BEGIN")
            cursor.execute(
                """
                INSERT INTO gehaltsgruppe (bezeichnung)
                VALUES (?)
                """,
                (p_gehaltsgruppe.bezeichnung,),
            )
            new_id = int(cursor.lastrowid)
            cursor.execute(
                """
                INSERT INTO gehaltsgruppe_betrag (gehaltsgruppe_id, betrag, gueltig_ab)
                VALUES (?, ?, ?)
                """,
                (new_id, p_betrag.betrag, p_betrag.gueltig_ab.isoformat()),
            )
            self._connection.commit()
        except Exception:
            self._connection.rollback()
            raise
        return Gehaltsgruppe(p_id=new_id, p_bezeichnung=p_gehaltsgruppe.bezeichnung)

    def exists(self, p_id: int) -> bool:
        cursor = self._connection.cursor()
        cursor.execute("SELECT 1 FROM gehaltsgruppe WHERE id = ?", (int(p_id),))
        return cursor.fetchone() is not None

    def add_betrag(self, p_betrag: GehaltsgruppenBetrag) -> None:
        cursor = self._connection.cursor()
        cursor.execute(
            """
            INSERT INTO gehaltsgruppe_betrag (gehaltsgruppe_id, betrag, gueltig_ab)
            VALUES (?, ?, ?)
            """,
            (
                p_betrag.gehaltsgruppe_id,
                p_betrag.betrag,
                p_betrag.gueltig_ab.isoformat(),
            ),
        )
        self._connection.commit()

    def get_all(self) -> list[Gehaltsgruppe]:
        cursor = self._connection.cursor()
        cursor.execute(
            """
            SELECT id, bezeichnung
            FROM gehaltsgruppe
            ORDER BY bezeichnung
            """
        )
        rows = cursor.fetchall()
        return [Gehaltsgruppe(p_id=row[0], p_bezeichnung=row[1]) for row in rows]

    def get_betrag_am_stichtag(self, p_group_id: int, p_stichtag: date) -> float | None:
        cursor = self._connection.cursor()
        cursor.execute(
            """
            SELECT betrag
            FROM gehaltsgruppe_betrag
            WHERE gehaltsgruppe_id = ?
              AND gueltig_ab <= ?
            ORDER BY gueltig_ab DESC
            LIMIT 1
            """,
            (int(p_group_id), p_stichtag.isoformat()),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return float(row[0])

    def get_betraege(self, p_group_id: int) -> list[dict[str, str | float]]:
        cursor = self._connection.cursor()
        cursor.execute(
            """
            SELECT betrag, gueltig_ab
            FROM gehaltsgruppe_betrag
            WHERE gehaltsgruppe_id = ?
            ORDER BY gueltig_ab ASC
            """,
            (int(p_group_id),),
        )
        rows = cursor.fetchall()
        return [
            {
                "betrag": float(row[0]),
                "gueltig_ab": str(row[1]),
            }
            for row in rows
        ]
