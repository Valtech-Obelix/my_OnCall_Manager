import sqlite3
from   pathlib                         import Path


DB_FILE_NAME                           = 'my_oncall_manager.db'


class Database:

    def __init__(self, p_db_path: Path | None = None):
        if p_db_path is None:
            p_db_path = Path(DB_FILE_NAME)

        self._connection = sqlite3.connect(p_db_path)
        self._connection.execute('PRAGMA foreign_keys = ON')

    def get_connection(self) -> sqlite3.Connection:
        return self._connection

    def close(self):
        if self._connection:
            self._connection.close()

    def initialize_schema(self):
        cursor = self._connection.cursor()

        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS incident_analyst (
                id                     INTEGER PRIMARY KEY AUTOINCREMENT,
                name                   TEXT NOT NULL,
                email                  TEXT NOT NULL UNIQUE
            )
            '''
        )

        self._connection.commit()
