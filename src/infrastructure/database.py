
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
                opsgenie_id     TEXT,
                start_datum     TEXT NOT NULL,
                ende_datum      TEXT
            )
            '''
        )

        # Ref: CR-007 – bestehende Daten erhalten und OpsGenieId nachrüsten
        self._ensure_incident_analyst_opsgenie_id_column()

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

        # Ref: CR-005 – Schichtplanstammdaten unabhängig von Import/Shift speichern
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS schedule_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schedule_id TEXT NOT NULL UNIQUE,
                schedule_name TEXT NOT NULL,
                last_used TEXT NOT NULL
            )
            '''
        )

        self._connection.commit()

    def _ensure_incident_analyst_opsgenie_id_column(self):
        cursor = self._connection.cursor()
        cursor.execute("PRAGMA table_info(incident_analyst)")
        columns = [row[1] for row in cursor.fetchall()]
        if "opsgenie_id" not in columns:
            cursor.execute("ALTER TABLE incident_analyst ADD COLUMN opsgenie_id TEXT")
