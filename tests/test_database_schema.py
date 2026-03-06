import sqlite3

from src.infrastructure.database import Database


def test_initialize_schema_adds_opsgenie_id_without_data_loss(tmp_path) -> None:
    db_path = tmp_path / "migration_test.db"

    connection = sqlite3.connect(db_path)
    connection.execute(
        """
        CREATE TABLE incident_analyst (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vornamen TEXT NOT NULL,
            nachname TEXT NOT NULL,
            buchungsname TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            start_datum TEXT NOT NULL,
            ende_datum TEXT
        )
        """
    )
    connection.execute(
        """
        INSERT INTO incident_analyst (
            vornamen, nachname, buchungsname, email, start_datum, ende_datum
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("Erika", "Mustermann", "Erika Mustermann", "erika@example.com", "2026-01-01", None),
    )
    connection.commit()
    connection.close()

    database = Database(p_db_path=db_path)
    database.initialize_schema()
    migrated_connection = database.get_connection()

    table_info = migrated_connection.execute(
        "PRAGMA table_info(incident_analyst)"
    ).fetchall()
    column_names = [row[1] for row in table_info]

    row = migrated_connection.execute(
        """
        SELECT vornamen, nachname, buchungsname, email, start_datum, ende_datum, opsgenie_id, oncall_location_id, mitarbeitertyp
        FROM incident_analyst
        """
    ).fetchone()

    assert "opsgenie_id" in column_names
    assert "oncall_location_id" in column_names
    assert "mitarbeitertyp" in column_names
    assert row == (
        "Erika",
        "Mustermann",
        "Erika Mustermann",
        "erika@example.com",
        "2026-01-01",
        None,
        None,
        "GER",
        "INCIDENT_ANALYST",
    )

    database.close()


def test_initialize_schema_removes_legacy_incident_analyst_columns(tmp_path) -> None:
    db_path = tmp_path / "legacy_incident_analyst_columns.db"

    connection = sqlite3.connect(db_path)
    connection.execute(
        """
        CREATE TABLE incident_analyst (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vornamen TEXT NOT NULL,
            nachname TEXT NOT NULL,
            buchungsname TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            opsgenie_id TEXT,
            oncall_location_id TEXT NOT NULL DEFAULT 'GER' CHECK (length(oncall_location_id) = 3),
            gehaltsgruppe TEXT,
            mitarbeiter_typ TEXT,
            start_datum TEXT NOT NULL,
            ende_datum TEXT
        )
        """
    )
    connection.execute(
        """
        INSERT INTO incident_analyst (
            vornamen, nachname, buchungsname, email, opsgenie_id, oncall_location_id, gehaltsgruppe, mitarbeiter_typ, start_datum, ende_datum
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "Erika",
            "Mustermann",
            "Mustermann, Erika",
            "erika@example.com",
            "ops-1",
            "GER",
            "A",
            "PRODUCT_OWNER",
            "2026-01-01",
            None,
        ),
    )
    connection.commit()
    connection.close()

    database = Database(p_db_path=db_path)
    database.initialize_schema()
    migrated_connection = database.get_connection()

    table_info = migrated_connection.execute("PRAGMA table_info(incident_analyst)").fetchall()
    column_names = [row[1] for row in table_info]

    assert "gehaltsgruppe" not in column_names
    assert "mitarbeiter_typ" not in column_names
    assert "mitarbeitertyp" in column_names

    row = migrated_connection.execute(
        """
        SELECT email, mitarbeitertyp
        FROM incident_analyst
        WHERE email = ?
        """,
        ("erika@example.com",),
    ).fetchone()
    assert row == ("erika@example.com", "PRODUCT_OWNER")

    database.close()


def test_initialize_schema_creates_entlohnungsklasse_table(tmp_path) -> None:
    db_path = tmp_path / "entlohnungsklasse_schema.db"
    database = Database(p_db_path=db_path)
    database.initialize_schema()
    connection = database.get_connection()

    table_info = connection.execute(
        "PRAGMA table_info(entlohnungsklasse)"
    ).fetchall()
    column_names = [row[1] for row in table_info]

    assert column_names == [
        "id",
        "typ",
        "beschreibung",
        "auszahlungsbetrag",
        "buchungstask_name",
    ]

    database.close()


def test_initialize_schema_creates_rufbereitschaftsstandort_table(tmp_path) -> None:
    db_path = tmp_path / "rufbereitschaftsstandort_schema.db"
    database = Database(p_db_path=db_path)
    database.initialize_schema()
    connection = database.get_connection()

    table_info = connection.execute(
        "PRAGMA table_info(rufbereitschaftsstandort)"
    ).fetchall()
    column_names = [row[1] for row in table_info]

    assert column_names == ["id", "name"]

    ger = connection.execute(
        "SELECT id, name FROM rufbereitschaftsstandort WHERE id = 'GER'"
    ).fetchone()
    assert ger == ("GER", "Deutschland")

    database.close()


def test_initialize_schema_creates_gehaltsgruppe_tables(tmp_path) -> None:
    db_path = tmp_path / "gehaltsgruppe_schema.db"
    database = Database(p_db_path=db_path)
    database.initialize_schema()
    connection = database.get_connection()

    group_table_info = connection.execute("PRAGMA table_info(gehaltsgruppe)").fetchall()
    group_columns = [row[1] for row in group_table_info]
    assert group_columns == ["id", "bezeichnung", "oncall_location_id"]

    amount_table_info = connection.execute(
        "PRAGMA table_info(gehaltsgruppe_betrag)"
    ).fetchall()
    amount_columns = [row[1] for row in amount_table_info]
    assert amount_columns == ["id", "gehaltsgruppe_id", "betrag", "gueltig_ab"]

    database.close()


def test_initialize_schema_creates_mitarbeiter_gehaltsgruppe_table(tmp_path) -> None:
    db_path = tmp_path / "mitarbeiter_gehaltsgruppe_schema.db"
    database = Database(p_db_path=db_path)
    database.initialize_schema()
    connection = database.get_connection()

    table_info = connection.execute(
        "PRAGMA table_info(mitarbeiter_gehaltsgruppe)"
    ).fetchall()
    column_names = [row[1] for row in table_info]

    assert column_names == [
        "id",
        "mitarbeiter_id",
        "gehaltsgruppe_id",
        "gueltig_ab",
        "gueltig_bis",
    ]

    database.close()


def test_initialize_schema_creates_budget_source_table(tmp_path) -> None:
    db_path = tmp_path / "budget_source_schema.db"
    database = Database(p_db_path=db_path)
    database.initialize_schema()
    connection = database.get_connection()

    table_info = connection.execute(
        "PRAGMA table_info(budget_source)"
    ).fetchall()
    column_names = [row[1] for row in table_info]

    assert column_names == ["id", "name", "is_active"]

    database.close()


def test_initialize_schema_creates_budget_period_table(tmp_path) -> None:
    db_path = tmp_path / "budget_period_schema.db"
    database = Database(p_db_path=db_path)
    database.initialize_schema()
    connection = database.get_connection()

    table_info = connection.execute(
        "PRAGMA table_info(budget_period)"
    ).fetchall()
    column_names = [row[1] for row in table_info]
    assert column_names == [
        "id",
        "budget_source_id",
        "gueltig_ab",
        "gueltig_bis",
        "betrag_eur",
        "note",
    ]

    fk_info = connection.execute("PRAGMA foreign_key_list(budget_period)").fetchall()
    assert any(
        row[2] == "budget_source" and row[3] == "budget_source_id"
        for row in fk_info
    )

    indexes = {
        row[1]: row[2] for row in connection.execute("PRAGMA index_list(budget_period)").fetchall()
    }
    assert any("idx_budget_period_source_from" in name for name in indexes)

    database.close()


def test_initialize_schema_repairs_legacy_foreign_keys_to_incident_analyst(tmp_path) -> None:
    db_path = tmp_path / "legacy_fk_repair.db"
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = OFF")

    connection.execute(
        """
        CREATE TABLE incident_analyst_legacy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vornamen TEXT NOT NULL,
            nachname TEXT NOT NULL,
            buchungsname TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            opsgenie_id TEXT,
            oncall_location_id TEXT NOT NULL DEFAULT 'GER',
            mitarbeitertyp TEXT NOT NULL DEFAULT 'INCIDENT_ANALYST',
            start_datum TEXT NOT NULL,
            ende_datum TEXT
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE incident_analyst (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vornamen TEXT NOT NULL,
            nachname TEXT NOT NULL,
            buchungsname TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            opsgenie_id TEXT,
            oncall_location_id TEXT NOT NULL DEFAULT 'GER',
            mitarbeitertyp TEXT NOT NULL DEFAULT 'INCIDENT_ANALYST',
            start_datum TEXT NOT NULL,
            ende_datum TEXT
        )
        """
    )
    connection.execute(
        """
        INSERT INTO incident_analyst (
            id, vornamen, nachname, buchungsname, email, start_datum
        )
        VALUES (1, 'Erika', 'Muster', 'Muster, Erika', 'erika@example.com', '2026-01-01')
        """
    )
    connection.execute(
        """
        CREATE TABLE gehaltsgruppe (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bezeichnung TEXT NOT NULL UNIQUE
        )
        """
    )
    connection.execute(
        """
        INSERT INTO gehaltsgruppe (id, bezeichnung)
        VALUES (1, 'A')
        """
    )
    connection.execute(
        """
        CREATE TABLE shifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analyst_id INTEGER NOT NULL,
            project TEXT NOT NULL,
            schedule_id TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            FOREIGN KEY (analyst_id) REFERENCES incident_analyst_legacy(id),
            UNIQUE (analyst_id, schedule_id, start_time, end_time)
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE mitarbeiter_gehaltsgruppe (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mitarbeiter_id INTEGER NOT NULL,
            gehaltsgruppe_id INTEGER NOT NULL,
            gueltig_ab TEXT NOT NULL,
            gueltig_bis TEXT,
            FOREIGN KEY (mitarbeiter_id) REFERENCES incident_analyst_legacy(id) ON DELETE CASCADE,
            FOREIGN KEY (gehaltsgruppe_id) REFERENCES gehaltsgruppe(id) ON DELETE RESTRICT
        )
        """
    )
    connection.commit()
    connection.close()

    database = Database(p_db_path=db_path)
    database.initialize_schema()
    migrated_connection = database.get_connection()

    shifts_fk = migrated_connection.execute("PRAGMA foreign_key_list(shifts)").fetchall()
    mitarbeiter_fk = migrated_connection.execute(
        "PRAGMA foreign_key_list(mitarbeiter_gehaltsgruppe)"
    ).fetchall()

    assert any(row[2] == "incident_analyst" for row in shifts_fk)
    assert not any(row[2] == "incident_analyst_legacy" for row in shifts_fk)
    assert any(row[2] == "incident_analyst" for row in mitarbeiter_fk)
    assert not any(row[2] == "incident_analyst_legacy" for row in mitarbeiter_fk)

    database.close()
