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
        SELECT vornamen, nachname, buchungsname, email, start_datum, ende_datum, opsgenie_id, oncall_location_id
        FROM incident_analyst
        """
    ).fetchone()

    assert "opsgenie_id" in column_names
    assert "oncall_location_id" in column_names
    assert row == (
        "Erika",
        "Mustermann",
        "Erika Mustermann",
        "erika@example.com",
        "2026-01-01",
        None,
        None,
        "GER",
    )

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
    assert group_columns == ["id", "bezeichnung"]

    amount_table_info = connection.execute(
        "PRAGMA table_info(gehaltsgruppe_betrag)"
    ).fetchall()
    amount_columns = [row[1] for row in amount_table_info]
    assert amount_columns == ["id", "gehaltsgruppe_id", "betrag", "gueltig_ab"]

    database.close()
