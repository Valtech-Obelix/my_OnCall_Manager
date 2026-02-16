import sqlite3
from   src.domain.incident_analyst     import IncidentAnalyst


TABLE_NAME                             = 'incident_analyst'


class IncidentAnalystRepository:

    def __init__(self, p_connection: sqlite3.Connection):
        self._connection = p_connection

    def add(self, p_analyst: IncidentAnalyst) -> IncidentAnalyst:
        cursor = self._connection.cursor()

        cursor.execute(
            f'''
            INSERT INTO {TABLE_NAME} (name, email)
            VALUES (?, ?)
            ''',
            (p_analyst.name, p_analyst.email)
        )

        self._connection.commit()

        new_id = cursor.lastrowid

        return IncidentAnalyst(  id    = new_id
                               , name  = p_analyst.name
                               , email = p_analyst.email
                              )
