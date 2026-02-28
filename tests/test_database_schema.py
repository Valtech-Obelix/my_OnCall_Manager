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
        SELECT vornamen, nachname, buchungsname, email, start_datum, ende_datum, opsgenie_id
        FROM incident_analyst
        """
    ).fetchone()

    assert "opsgenie_id" in column_names
    assert row == (
        "Erika",
        "Mustermann",
        "Erika Mustermann",
        "erika@example.com",
        "2026-01-01",
        None,
        None,
    )

    database.close()
