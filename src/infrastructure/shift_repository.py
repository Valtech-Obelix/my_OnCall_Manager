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

    def save_import_history(
        self,
        p_schedule_id: str,
        p_schedule_name: str
    ) -> None:
        source = self._to_history_source(
            p_schedule_id=p_schedule_id,
            p_schedule_name=p_schedule_name
        )

        cursor = self._connection.cursor()
        cursor.execute(
            '''
            INSERT INTO import_history (source, last_import)
            VALUES (?, datetime('now'))
            ON CONFLICT(source)
            DO UPDATE SET last_import = excluded.last_import
            ''',
            (source,)
        )
        self._connection.commit()

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

    def get_import_history(self) -> list[dict[str, str]]:
        cursor = self._connection.cursor()
        cursor.execute(
            '''
            SELECT source, last_import
            FROM import_history
            ORDER BY datetime(last_import) DESC
            '''
        )

        entries: list[dict[str, str]] = []
        for source, last_import in cursor.fetchall():
            schedule_id, schedule_name = self._from_history_source(source)
            entries.append(
                {
                    "schedule_id": schedule_id,
                    "schedule_name": schedule_name,
                    "last_import": last_import,
                }
            )
        return entries

    def has_import_history_for_schedule(self, p_schedule_id: str) -> bool:
        cursor = self._connection.cursor()
        cursor.execute(
            '''
            SELECT 1
            FROM import_history
            WHERE source = ?
               OR source LIKE ?
            LIMIT 1
            ''',
            (p_schedule_id, f"{p_schedule_id}|%")
        )
        return cursor.fetchone() is not None

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

    def _to_history_source(
        self,
        p_schedule_id: str,
        p_schedule_name: str
    ) -> str:
        return f"{p_schedule_id}|{p_schedule_name}"

    def _from_history_source(self, p_source: str) -> tuple[str, str]:
        if "|" in p_source:
            schedule_id, schedule_name = p_source.split("|", 1)
            return schedule_id, schedule_name
        # Fallback für alte Datensätze ohne Namensanteil
        return p_source, ""
