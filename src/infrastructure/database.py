
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
                mitarbeitertyp  TEXT NOT NULL DEFAULT 'INCIDENT_ANALYST'
                                    CHECK (mitarbeitertyp IN ('INCIDENT_ANALYST', 'PRODUCT_OWNER', 'SONSTIGE')),
                start_datum     TEXT NOT NULL,
                ende_datum      TEXT
            )
            '''
        )

        # Ref: CR-007 – bestehende Daten erhalten und OpsGenieId nachrüsten
        self._ensure_incident_analyst_opsgenie_id_column()
        self._ensure_incident_analyst_oncall_location_id_column()
        self._ensure_incident_analyst_mitarbeitertyp_column()
        self._normalize_incident_analyst_schema()

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

        # Ref: UC-019 v0.2 – Aktivierungsverlauf pro Mitarbeiter
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS mitarbeiter_aktivierung (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mitarbeiter_id INTEGER NOT NULL,
                start_datum TEXT NOT NULL,
                ende_datum TEXT,
                FOREIGN KEY (mitarbeiter_id) REFERENCES incident_analyst(id) ON DELETE CASCADE,
                CHECK (ende_datum IS NULL OR ende_datum >= start_datum)
            )
            '''
        )
        cursor.execute(
            '''
            CREATE INDEX IF NOT EXISTS idx_mitarbeiter_aktivierung_lookup
            ON mitarbeiter_aktivierung (mitarbeiter_id, start_datum DESC)
            '''
        )

        # Ref: UC-019 v0.1 – Gehaltsklassenzuordnung zu Mitarbeitern (historisiert)
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS mitarbeiter_gehaltsgruppe (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mitarbeiter_id INTEGER NOT NULL,
                gehaltsgruppe_id INTEGER NOT NULL,
                gueltig_ab TEXT NOT NULL,
                gueltig_bis TEXT,
                FOREIGN KEY (mitarbeiter_id) REFERENCES incident_analyst(id) ON DELETE CASCADE,
                FOREIGN KEY (gehaltsgruppe_id) REFERENCES gehaltsgruppe(id) ON DELETE RESTRICT,
                CHECK (gueltig_bis IS NULL OR gueltig_bis >= gueltig_ab)
            )
            '''
        )
        cursor.execute(
            '''
            CREATE INDEX IF NOT EXISTS idx_mitarbeiter_gehaltsgruppe_lookup
            ON mitarbeiter_gehaltsgruppe (mitarbeiter_id, gueltig_ab DESC)
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

        # Ref: UC-017 v0.1 – Gehaltsgruppen mit historisierten Betraegen
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS gehaltsgruppe (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bezeichnung TEXT NOT NULL UNIQUE CHECK (length(trim(bezeichnung)) > 0),
                oncall_location_id TEXT NOT NULL DEFAULT 'GER' CHECK (length(oncall_location_id) = 3)
            )
            '''
        )
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS gehaltsgruppe_betrag (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gehaltsgruppe_id INTEGER NOT NULL,
                betrag REAL NOT NULL CHECK (betrag >= 0),
                gueltig_ab TEXT NOT NULL,
                FOREIGN KEY (gehaltsgruppe_id) REFERENCES gehaltsgruppe(id) ON DELETE CASCADE,
                UNIQUE (gehaltsgruppe_id, gueltig_ab)
            )
            '''
        )
        cursor.execute(
            '''
            CREATE INDEX IF NOT EXISTS idx_gehaltsgruppe_betrag_lookup
            ON gehaltsgruppe_betrag (gehaltsgruppe_id, gueltig_ab DESC)
            '''
        )

        # Ref: UC-021 – Budgetquellen (z. B. Kunde/Partner/Projekt)
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS budget_source (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE CHECK (length(trim(name)) > 0),
                is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
            )
            '''
        )

        # Ref: UC-021 – Budgetzeiträume je Quelle
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS budget_period (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                budget_source_id INTEGER NOT NULL,
                gueltig_ab TEXT NOT NULL,
                gueltig_bis TEXT,
                betrag_eur REAL NOT NULL CHECK (betrag_eur >= 0),
                note TEXT,
                FOREIGN KEY (budget_source_id)
                    REFERENCES budget_source (id)
                    ON DELETE CASCADE,
                CHECK (gueltig_bis IS NULL OR gueltig_bis >= gueltig_ab)
            )
            '''
        )
        cursor.execute(
            '''
            CREATE INDEX IF NOT EXISTS idx_budget_period_source_from
            ON budget_period (budget_source_id, gueltig_ab)
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
        self._ensure_gehaltsgruppe_oncall_location_id_column()
        self._repair_incident_analyst_foreign_keys()
        self._seed_activation_periods_from_incident_analyst()

        # Legacy cleanup: import_history wird nicht mehr verwendet.
        cursor.execute("DROP TABLE IF EXISTS import_history")
        cursor.execute("DROP TABLE IF EXISTS salary_group_rate")
        cursor.execute("DROP TABLE IF EXISTS employee_salary_group_assignment")
        cursor.execute("DROP TABLE IF EXISTS salary_group")
        cursor.execute("DROP TABLE IF EXISTS budget_cost_rate")

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

    def _ensure_incident_analyst_mitarbeitertyp_column(self):
        cursor = self._connection.cursor()
        cursor.execute("PRAGMA table_info(incident_analyst)")
        columns = [row[1] for row in cursor.fetchall()]
        if "mitarbeitertyp" not in columns:
            cursor.execute(
                "ALTER TABLE incident_analyst "
                "ADD COLUMN mitarbeitertyp TEXT NOT NULL DEFAULT 'INCIDENT_ANALYST' "
                "CHECK (mitarbeitertyp IN ('INCIDENT_ANALYST', 'PRODUCT_OWNER', 'SONSTIGE'))"
            )
            cursor.execute(
                "UPDATE incident_analyst "
                "SET mitarbeitertyp = 'INCIDENT_ANALYST' "
                "WHERE mitarbeitertyp IS NULL OR trim(mitarbeitertyp) = ''"
            )

    def _ensure_gehaltsgruppe_oncall_location_id_column(self):
        cursor = self._connection.cursor()
        cursor.execute("PRAGMA table_info(gehaltsgruppe)")
        columns = [row[1] for row in cursor.fetchall()]
        if "oncall_location_id" in columns:
            return

        cursor.execute(
            "ALTER TABLE gehaltsgruppe "
            "ADD COLUMN oncall_location_id TEXT NOT NULL DEFAULT 'GER' CHECK (length(oncall_location_id) = 3)"
        )
        cursor.execute(
            "UPDATE gehaltsgruppe "
            "SET oncall_location_id = 'GER' "
            "WHERE oncall_location_id IS NULL OR trim(oncall_location_id) = ''"
        )
        self._connection.commit()

    def _normalize_incident_analyst_schema(self):
        cursor = self._connection.cursor()
        table_names = {
            row[0]
            for row in cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }

        source_table = None
        if "incident_analyst_legacy" in table_names:
            source_table = "incident_analyst_legacy"
        elif "incident_analyst" in table_names:
            cursor.execute("PRAGMA table_info(incident_analyst)")
            columns = [row[1] for row in cursor.fetchall()]
            legacy_columns = {"gehaltsgruppe", "mitarbeiter_typ"}
            if legacy_columns.intersection(columns):
                source_table = "incident_analyst"

        if source_table is None:
            return

        fk_state = cursor.execute("PRAGMA foreign_keys").fetchone()
        foreign_keys_enabled = bool(fk_state[0]) if fk_state else True

        if foreign_keys_enabled:
            cursor.execute("PRAGMA foreign_keys = OFF")

        try:
            if source_table == "incident_analyst":
                cursor.execute("ALTER TABLE incident_analyst RENAME TO incident_analyst_legacy")
                source_table = "incident_analyst_legacy"

            cursor.execute("DROP TABLE IF EXISTS incident_analyst")
            cursor.execute(
                '''
                CREATE TABLE incident_analyst (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    vornamen        TEXT NOT NULL,
                    nachname        TEXT NOT NULL,
                    buchungsname    TEXT NOT NULL,
                    email           TEXT NOT NULL UNIQUE,
                    opsgenie_id     TEXT,
                    oncall_location_id TEXT NOT NULL DEFAULT 'GER' CHECK (length(oncall_location_id) = 3),
                    mitarbeitertyp  TEXT NOT NULL DEFAULT 'INCIDENT_ANALYST'
                                        CHECK (mitarbeitertyp IN ('INCIDENT_ANALYST', 'PRODUCT_OWNER', 'SONSTIGE')),
                    start_datum     TEXT NOT NULL,
                    ende_datum      TEXT
                )
                '''
            )

            source_columns = {
                row[1]
                for row in cursor.execute(f"PRAGMA table_info({source_table})").fetchall()
            }

            opsgenie_expr = "opsgenie_id" if "opsgenie_id" in source_columns else "NULL"
            oncall_expr = (
                "CASE "
                "WHEN oncall_location_id IS NULL OR trim(oncall_location_id) = '' THEN 'GER' "
                "ELSE upper(trim(oncall_location_id)) "
                "END"
                if "oncall_location_id" in source_columns
                else "'GER'"
            )

            if "mitarbeiter_typ" in source_columns and "mitarbeitertyp" in source_columns:
                raw_typ_expr = (
                    "COALESCE(NULLIF(trim(mitarbeiter_typ), ''), NULLIF(trim(mitarbeitertyp), ''), 'INCIDENT_ANALYST')"
                )
            elif "mitarbeiter_typ" in source_columns:
                raw_typ_expr = "COALESCE(NULLIF(trim(mitarbeiter_typ), ''), 'INCIDENT_ANALYST')"
            elif "mitarbeitertyp" in source_columns:
                raw_typ_expr = "COALESCE(NULLIF(trim(mitarbeitertyp), ''), 'INCIDENT_ANALYST')"
            else:
                raw_typ_expr = "'INCIDENT_ANALYST'"

            typ_expr = (
                "CASE "
                f"WHEN upper({raw_typ_expr}) IN ('INCIDENT_ANALYST', 'PRODUCT_OWNER', 'SONSTIGE') THEN upper({raw_typ_expr}) "
                f"WHEN upper({raw_typ_expr}) = 'PO' OR upper({raw_typ_expr}) LIKE '%OWNER%' THEN 'PRODUCT_OWNER' "
                f"WHEN upper({raw_typ_expr}) LIKE '%SONST%' THEN 'SONSTIGE' "
                "ELSE 'INCIDENT_ANALYST' "
                "END"
            )

            cursor.execute(
                f'''
                INSERT INTO incident_analyst
                (
                    id,
                    vornamen,
                    nachname,
                    buchungsname,
                    email,
                    opsgenie_id,
                    oncall_location_id,
                    mitarbeitertyp,
                    start_datum,
                    ende_datum
                )
                SELECT
                    id,
                    vornamen,
                    nachname,
                    buchungsname,
                    email,
                    {opsgenie_expr},
                    {oncall_expr},
                    {typ_expr},
                    start_datum,
                    ende_datum
                FROM {source_table}
                '''
            )
            cursor.execute("DROP TABLE IF EXISTS incident_analyst_legacy")
            self._connection.commit()
        except Exception:
            self._connection.rollback()
            raise
        finally:
            if foreign_keys_enabled:
                cursor.execute("PRAGMA foreign_keys = ON")

    def _ensure_default_oncall_location(self):
        cursor = self._connection.cursor()
        cursor.execute(
            '''
            INSERT OR IGNORE INTO rufbereitschaftsstandort (id, name)
            VALUES ('GER', 'Deutschland')
            '''
        )

    def _repair_incident_analyst_foreign_keys(self):
        cursor = self._connection.cursor()
        self._rebuild_shifts_if_legacy_fk(cursor)
        self._rebuild_mitarbeiter_gehaltsgruppe_if_legacy_fk(cursor)

    def _seed_activation_periods_from_incident_analyst(self):
        cursor = self._connection.cursor()
        cursor.execute(
            '''
            INSERT INTO mitarbeiter_aktivierung (mitarbeiter_id, start_datum, ende_datum)
            SELECT ia.id, ia.start_datum, ia.ende_datum
            FROM incident_analyst ia
            WHERE ia.start_datum IS NOT NULL
              AND trim(ia.start_datum) != ''
              AND NOT EXISTS (
                    SELECT 1
                    FROM mitarbeiter_aktivierung ma
                    WHERE ma.mitarbeiter_id = ia.id
              )
            '''
        )

    def _rebuild_shifts_if_legacy_fk(self, p_cursor: sqlite3.Cursor) -> None:
        p_cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='shifts'"
        )
        if p_cursor.fetchone() is None:
            return

        p_cursor.execute("PRAGMA foreign_key_list(shifts)")
        fks = p_cursor.fetchall()
        if not any(row[2] == "incident_analyst_legacy" for row in fks):
            return

        p_cursor.execute("ALTER TABLE shifts RENAME TO shifts_legacy_fk")
        p_cursor.execute(
            '''
            CREATE TABLE shifts (
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
        p_cursor.execute(
            '''
            INSERT INTO shifts (id, analyst_id, project, schedule_id, start_time, end_time)
            SELECT id, analyst_id, project, schedule_id, start_time, end_time
            FROM shifts_legacy_fk
            '''
        )
        p_cursor.execute("DROP TABLE shifts_legacy_fk")

    def _rebuild_mitarbeiter_gehaltsgruppe_if_legacy_fk(self, p_cursor: sqlite3.Cursor) -> None:
        p_cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='mitarbeiter_gehaltsgruppe'"
        )
        if p_cursor.fetchone() is None:
            return

        p_cursor.execute("PRAGMA foreign_key_list(mitarbeiter_gehaltsgruppe)")
        fks = p_cursor.fetchall()
        if not any(row[2] == "incident_analyst_legacy" for row in fks):
            return

        p_cursor.execute("ALTER TABLE mitarbeiter_gehaltsgruppe RENAME TO mitarbeiter_gehaltsgruppe_legacy_fk")
        p_cursor.execute(
            '''
            CREATE TABLE mitarbeiter_gehaltsgruppe (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mitarbeiter_id INTEGER NOT NULL,
                gehaltsgruppe_id INTEGER NOT NULL,
                gueltig_ab TEXT NOT NULL,
                gueltig_bis TEXT,
                FOREIGN KEY (mitarbeiter_id) REFERENCES incident_analyst(id) ON DELETE CASCADE,
                FOREIGN KEY (gehaltsgruppe_id) REFERENCES gehaltsgruppe(id) ON DELETE RESTRICT,
                CHECK (gueltig_bis IS NULL OR gueltig_bis >= gueltig_ab)
            )
            '''
        )
        p_cursor.execute(
            '''
            INSERT INTO mitarbeiter_gehaltsgruppe
            (id, mitarbeiter_id, gehaltsgruppe_id, gueltig_ab, gueltig_bis)
            SELECT id, mitarbeiter_id, gehaltsgruppe_id, gueltig_ab, gueltig_bis
            FROM mitarbeiter_gehaltsgruppe_legacy_fk
            '''
        )
        p_cursor.execute("DROP TABLE mitarbeiter_gehaltsgruppe_legacy_fk")
        p_cursor.execute(
            '''
            CREATE INDEX IF NOT EXISTS idx_mitarbeiter_gehaltsgruppe_lookup
            ON mitarbeiter_gehaltsgruppe (mitarbeiter_id, gueltig_ab DESC)
            '''
        )
