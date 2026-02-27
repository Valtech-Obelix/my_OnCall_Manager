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
