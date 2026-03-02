import sqlite3


class OnCallLocationRepository:
    def __init__(self, p_connection: sqlite3.Connection):
        self._connection = p_connection

    def get_all(self) -> list[dict[str, str]]:
        cursor = self._connection.cursor()
        cursor.execute(
            '''
            SELECT id, name
            FROM rufbereitschaftsstandort
            ORDER BY id ASC
            '''
        )
        rows = cursor.fetchall()
        return [{"id": row[0], "name": row[1]} for row in rows]

    def exists(self, p_id: str) -> bool:
        cursor = self._connection.cursor()
        cursor.execute(
            '''
            SELECT 1
            FROM rufbereitschaftsstandort
            WHERE id = ?
            LIMIT 1
            ''',
            (p_id,)
        )
        return cursor.fetchone() is not None

    def add(self, p_id: str, p_name: str) -> None:
        cursor = self._connection.cursor()
        cursor.execute(
            '''
            INSERT INTO rufbereitschaftsstandort (id, name)
            VALUES (?, ?)
            ''',
            (p_id, p_name)
        )
        self._connection.commit()

    def update(self, p_original_id: str, p_new_id: str, p_name: str) -> None:
        cursor = self._connection.cursor()
        cursor.execute(
            '''
            UPDATE rufbereitschaftsstandort
            SET id = ?, name = ?
            WHERE id = ?
            ''',
            (p_new_id, p_name, p_original_id)
        )
        self._connection.commit()

    def delete(self, p_id: str) -> None:
        cursor = self._connection.cursor()
        cursor.execute(
            '''
            DELETE FROM rufbereitschaftsstandort
            WHERE id = ?
            ''',
            (p_id,)
        )
        self._connection.commit()
