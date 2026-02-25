
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

        # Ref: UC-001 v0.2 – erweitertes Datenmodell IncidentAnalyst
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS incident_analyst (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                vornamen        TEXT NOT NULL,
                nachname        TEXT NOT NULL,
                buchungsname    TEXT NOT NULL,
                email           TEXT NOT NULL UNIQUE,
                start_datum     TEXT NOT NULL,
                ende_datum      TEXT
            )
            '''
        )

        # Ref: UC-004 v0.1 – Shift Tabelle
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS shifts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analyst_id INTEGER NOT NULL,
                project TEXT NOT NULL,
                schedule_id TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                FOREIGN KEY (analyst_id) REFERENCES incident_analyst(id),
                UNIQUE (analyst_id, schedule_id, start_time, end_time)
            )
            '''
        )

        # Ref: UC-004 v0.1 – Import History
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS import_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL UNIQUE,
                last_import TEXT NOT NULL
            )
            '''
        )

        self._connection.commit()
