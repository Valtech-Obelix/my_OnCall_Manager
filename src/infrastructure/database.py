
import sqlite3
import shutil
from   pathlib                         import Path
from   src.infrastructure.runtime_paths import db_file_path, seed_db_path

class Database:

    def __init__(self, p_db_path: Path | None = None):
        if p_db_path is None:
            p_db_path = db_file_path()
            self._copy_seed_db_if_missing(p_db_path)

        self._connection = sqlite3.connect(p_db_path)
        self._connection.execute('PRAGMA foreign_keys = ON')

    def _copy_seed_db_if_missing(self, p_target_db_path: Path) -> None:
        if p_target_db_path.exists():
            return
        seed_path = seed_db_path()
        if seed_path is None:
            return
        p_target_db_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(seed_path, p_target_db_path)

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
                oncall_location_id TEXT NOT NULL DEFAULT 'GER' CHECK (length(oncall_location_id) = 3),
                start_datum     TEXT NOT NULL,
                ende_datum      TEXT
            )
            '''
        )

        # Ref: CR-007 – bestehende Daten erhalten und OpsGenieId nachrüsten
        self._ensure_incident_analyst_opsgenie_id_column()
        self._ensure_incident_analyst_oncall_location_id_column()

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
        self._ensure_default_oncall_location()

        # Legacy cleanup: import_history wird nicht mehr verwendet.
        cursor.execute("DROP TABLE IF EXISTS import_history")

        self._connection.commit()

    def _ensure_incident_analyst_opsgenie_id_column(self):
        cursor = self._connection.cursor()
        cursor.execute("PRAGMA table_info(incident_analyst)")
        columns = [row[1] for row in cursor.fetchall()]
        if "opsgenie_id" not in columns:
            cursor.execute("ALTER TABLE incident_analyst ADD COLUMN opsgenie_id TEXT")

    def _ensure_incident_analyst_oncall_location_id_column(self):
        cursor = self._connection.cursor()
        cursor.execute("PRAGMA table_info(incident_analyst)")
        columns = [row[1] for row in cursor.fetchall()]
        if "oncall_location_id" not in columns:
            cursor.execute(
                "ALTER TABLE incident_analyst "
                "ADD COLUMN oncall_location_id TEXT NOT NULL DEFAULT 'GER' "
                "CHECK (length(oncall_location_id) = 3)"
            )
            cursor.execute(
                "UPDATE incident_analyst "
                "SET oncall_location_id = 'GER' "
                "WHERE oncall_location_id IS NULL OR trim(oncall_location_id) = ''"
            )

    def _ensure_default_oncall_location(self):
        cursor = self._connection.cursor()
        cursor.execute(
            '''
            INSERT OR IGNORE INTO rufbereitschaftsstandort (id, name)
            VALUES ('GER', 'Deutschland')
            '''
        )
