import   sqlite3
from     src.domain.shift                                  import Shift


class ShiftRepository:

    def __init__(self, p_connection):
        self._connection = p_connection

    def save(self, p_shift: Shift) -> bool:
        """
        Speichert eine Schicht.
        Returns:
            True  -> neu gespeichert
            False -> bereits vorhanden (Duplikat)
        """

        try:
            cursor = self._connection.cursor()

            cursor.execute(
                '''
                INSERT INTO shifts (
                    analyst_id,
                    project,
                    schedule_id,
                    start_time,
                    end_time
                )
                VALUES (?, ?, ?, ?, ?)
                ''',
                (
                    p_shift.analyst_id,
                    p_shift.project,
                    p_shift.schedule_id,
                    p_shift.start_time,
                    p_shift.end_time
                )
            )

            self._connection.commit()
            return True

        except sqlite3.IntegrityError:
            # Duplikat aufgrund UNIQUE-Constraint
            return False

    def save_schedule_reference(
        self,
        p_schedule_id: str,
        p_schedule_name: str
    ) -> None:
        cursor = self._connection.cursor()
        cursor.execute(
            '''
            INSERT INTO schedule_registry (
                schedule_id,
                schedule_name,
                last_used
            )
            VALUES (?, ?, datetime('now'))
            ON CONFLICT(schedule_id)
            DO UPDATE SET
                schedule_name = excluded.schedule_name,
                last_used = excluded.last_used
            ''',
            (p_schedule_id, p_schedule_name)
        )
        self._connection.commit()

    def get_schedule_references(self) -> list[dict[str, str]]:
        cursor = self._connection.cursor()
        cursor.execute(
            '''
            SELECT schedule_id, schedule_name, last_used
            FROM schedule_registry
            ORDER BY datetime(last_used) DESC
            '''
        )

        entries: list[dict[str, str]] = []
        for schedule_id, schedule_name, last_used in cursor.fetchall():
            entries.append(
                {
                    "schedule_id": schedule_id,
                    "schedule_name": schedule_name,
                    "last_used": last_used,
                }
            )
        return entries

    def get_schedule_time_bounds(
        self,
        p_schedule_id: str
    ) -> tuple[str | None, str | None]:
        cursor = self._connection.cursor()
        cursor.execute(
            '''
            SELECT MIN(start_time), MAX(end_time)
            FROM shifts
            WHERE schedule_id = ?
            ''',
            (p_schedule_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return None, None
        return row[0], row[1]

    def get_schedule_entries(self, p_schedule_id: str) -> list[dict[str, str | int | None]]:
        cursor = self._connection.cursor()
        cursor.execute(
            '''
            SELECT
                s.id,
                s.schedule_id,
                s.project,
                s.start_time,
                s.end_time,
                ia.buchungsname,
                ia.email
            FROM shifts s
            LEFT JOIN incident_analyst ia ON ia.id = s.analyst_id
            WHERE s.schedule_id = ?
            ORDER BY s.start_time ASC
            ''',
            (p_schedule_id,)
        )

        entries: list[dict[str, str | int | None]] = []
        for row in cursor.fetchall():
            entries.append(
                {
                    "id": row[0],
                    "schedule_id": row[1],
                    "project": row[2],
                    "start_time": row[3],
                    "end_time": row[4],
                    "buchungsname": row[5],
                    "email": row[6],
                }
            )
        return entries

    def get_schedule_shift_starts(
        self,
        p_schedule_id: str
    ) -> list[tuple[int, str]]:
        cursor = self._connection.cursor()
        cursor.execute(
            '''
            SELECT analyst_id, start_time
            FROM shifts
            WHERE schedule_id = ?
            ''',
            (p_schedule_id,)
        )
        return [(int(row[0]), str(row[1])) for row in cursor.fetchall()]

    def get_active_analyst_shift_counts_last_weeks(
        self,
        p_weeks: int
    ) -> list[dict[str, str | int]]:
        cursor = self._connection.cursor()
        days = max(1, int(p_weeks)) * 7
        cursor.execute(
            '''
            SELECT
                ia.buchungsname,
                COUNT(s.id) AS shift_count
            FROM incident_analyst ia
            LEFT JOIN shifts s
                ON s.analyst_id = ia.id
               AND datetime(replace(replace(s.start_time, 'T', ' '), 'Z', ''))
                   >= datetime('now', ?)
               AND datetime(replace(replace(s.start_time, 'T', ' '), 'Z', ''))
                   < datetime('now')
            WHERE ia.ende_datum IS NULL
            GROUP BY ia.id, ia.buchungsname
            ORDER BY shift_count DESC, ia.buchungsname ASC
            ''',
            (f'-{days} days',)
        )

        entries: list[dict[str, str | int]] = []
        for buchungsname, shift_count in cursor.fetchall():
            entries.append(
                {
                    "buchungsname": buchungsname,
                    "shift_count": int(shift_count),
                }
            )
        return entries

    def get_setting(self, p_key: str) -> str | None:
        cursor = self._connection.cursor()
        cursor.execute(
            '''
            SELECT value
            FROM app_settings
            WHERE key = ?
            ''',
            (p_key,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return row[0]

    def set_setting(self, p_key: str, p_value: str) -> None:
        cursor = self._connection.cursor()
        cursor.execute(
            '''
            INSERT INTO app_settings (key, value)
            VALUES (?, ?)
            ON CONFLICT(key)
            DO UPDATE SET value = excluded.value
            ''',
            (p_key, p_value)
        )
        self._connection.commit()
