from datetime import datetime
from typing import List
import sqlite3

from src.domain.shift import Shift


class ShiftRepository:
    """
    Ref: UC-004 v0.1
    - Persistenz für OpsGenie Shifts
    - Verwaltung Import-Zeitpunkt
    """

    def __init__(self, p_connection: sqlite3.Connection):
        self._connection = p_connection

    # ----------------------------
    # Shift Speicherung
    # ----------------------------

    def add(self, p_shift: Shift) -> Shift:
        cursor = self._connection.cursor()

        cursor.execute(
            '''
            INSERT INTO shifts (project, schedule_id, analyst_name, start_time, end_time)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (
                p_shift.project,
                p_shift.schedule_id,
                p_shift.analyst_name,
                p_shift.start.isoformat(),
                p_shift.end.isoformat()
            )
        )

        self._connection.commit()

        new_id = cursor.lastrowid

        return Shift(
            p_id=new_id,
            p_project=p_shift.project,
            p_schedule_id=p_shift.schedule_id,
            p_analyst_name=p_shift.analyst_name,
            p_start=p_shift.start,
            p_end=p_shift.end
        )

    def add_many(self, p_shifts: List[Shift]) -> None:
        cursor = self._connection.cursor()

        cursor.executemany(
            '''
            INSERT INTO shifts (project, schedule_id, analyst_name, start_time, end_time)
            VALUES (?, ?, ?, ?, ?)
            ''',
            [
                (
                    s.project,
                    s.schedule_id,
                    s.analyst_name,
                    s.start.isoformat(),
                    s.end.isoformat()
                )
                for s in p_shifts
            ]
        )

        self._connection.commit()

    # ----------------------------
    # Import History
    # ----------------------------

    def get_last_import(self, p_source: str) -> datetime | None:
        cursor = self._connection.cursor()

        cursor.execute(
            '''
            SELECT last_import FROM import_history
            WHERE source = ?
            ''',
            (p_source,)
        )

        row = cursor.fetchone()

        if not row:
            return None

        return datetime.fromisoformat(row[0])

    def set_last_import(self, p_source: str, p_timestamp: datetime) -> None:
        cursor = self._connection.cursor()

        cursor.execute(
            '''
            INSERT INTO import_history (source, last_import)
            VALUES (?, ?)
            ON CONFLICT(source)
            DO UPDATE SET last_import = excluded.last_import
            ''',
            (p_source, p_timestamp.isoformat())
        )

        self._connection.commit()