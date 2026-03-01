import sqlite3

from src.infrastructure.oncall_location_repository import OnCallLocationRepository


def _create_repository() -> OnCallLocationRepository:
    connection = sqlite3.connect(":memory:")
    connection.execute(
        """
        CREATE TABLE rufbereitschaftsstandort (
            id TEXT PRIMARY KEY CHECK (length(id) = 3),
            name TEXT NOT NULL CHECK (length(name) BETWEEN 1 AND 30)
        )
        """
    )
    return OnCallLocationRepository(connection)


def test_add_and_get_all() -> None:
    repository = _create_repository()
    repository.add("MUC", "Muenchen")

    rows = repository.get_all()

    assert rows == [{"id": "MUC", "name": "Muenchen"}]


def test_update_allows_changing_id_and_name() -> None:
    repository = _create_repository()
    repository.add("MUC", "Muenchen")

    repository.update("MUC", "BER", "Berlin")

    rows = repository.get_all()
    assert rows == [{"id": "BER", "name": "Berlin"}]


def test_exists_and_delete() -> None:
    repository = _create_repository()
    repository.add("FRA", "Frankfurt")

    assert repository.exists("FRA") is True
    repository.delete("FRA")
    assert repository.exists("FRA") is False
