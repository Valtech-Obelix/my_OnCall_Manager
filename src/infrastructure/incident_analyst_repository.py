import sqlite3
from   src.domain.incident_analyst     import IncidentAnalyst


TABLE_NAME                             = 'incident_analyst'


class IncidentAnalystRepository:

    def __init__(self, p_connection: sqlite3.Connection):
        self._connection = p_connection


    def add(self, p_analyst: IncidentAnalyst) -> IncidentAnalyst:

        cursor = self._connection.cursor()

        # Ref: UC-001 v0.2 – erweiterte Persistenzstruktur
        cursor.execute(
            f'''
            INSERT INTO {TABLE_NAME}
            (vorname, nachname, buchungsname, email, start_datum, end_datum)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (
                p_analyst.vorname,
                p_analyst.nachname,
                p_analyst.buchungsname,
                p_analyst.email,
                p_analyst.start_datum.isoformat(),
                p_analyst.end_datum.isoformat()
                if p_analyst.end_datum
                else None
            )
        )

        self._connection.commit()

        new_id = cursor.lastrowid

        # Neues Objekt mit gesetzter ID zurückgeben
        return IncidentAnalyst(
            p_id=new_id,
            p_vorname=p_analyst.vorname,
            p_nachname=p_analyst.nachname,
            p_email=p_analyst.email,
            p_start_datum=p_analyst.start_datum,
            p_end_datum=p_analyst.end_datum
        )