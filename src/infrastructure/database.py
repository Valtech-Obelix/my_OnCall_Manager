
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

        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            '''
        )

        # Ref: UC-010 v0.1 – Entlohnungsklassen speichern (Schritt 1)
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS entlohnungsklasse (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                typ TEXT NOT NULL,
                beschreibung TEXT NOT NULL,
                auszahlungsbetrag REAL NOT NULL CHECK (auszahlungsbetrag >= 0),
                buchungstask_name TEXT NOT NULL
            )
            '''
        )

        # Ref: UC-011 v0.1 – Rufbereitschaftsstandorte
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS rufbereitschaftsstandort (
                id TEXT PRIMARY KEY CHECK (length(id) = 3),
                name TEXT NOT NULL CHECK (length(name) BETWEEN 1 AND 30)
            )
            '''
        )

        # Legacy cleanup: import_history wird nicht mehr verwendet.
        cursor.execute("DROP TABLE IF EXISTS import_history")

        self._connection.commit()

    def _ensure_incident_analyst_opsgenie_id_column(self):
        cursor = self._connection.cursor()
        cursor.execute("PRAGMA table_info(incident_analyst)")
        columns = [row[1] for row in cursor.fetchall()]
        if "opsgenie_id" not in columns:
            cursor.execute("ALTER TABLE incident_analyst ADD COLUMN opsgenie_id TEXT")
