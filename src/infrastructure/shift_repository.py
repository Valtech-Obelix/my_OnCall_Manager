import   sqlite3
from     datetime                                          import datetime
from     typing                                            import (  List
                                                                   , Optional
                                                                  )
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