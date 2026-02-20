import   sqlite3
from     src.domain.incident_analyst                  import IncidentAnalyst
from     datetime                                     import date


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
            (vornamen, nachname, buchungsname, email, start_datum, ende_datum)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (
                p_analyst.vornamen,
                p_analyst.nachname,
                p_analyst.buchungsname,
                p_analyst.email,
                p_analyst.start_datum.isoformat(),
                p_analyst.ende_datum.isoformat()
                if p_analyst.ende_datum
                else None
            )
        )

        self._connection.commit()

        new_id = cursor.lastrowid

        # Neues Objekt mit gesetzter ID zurückgeben
        return IncidentAnalyst(p_id          = new_id, 
                               p_vornamen    = p_analyst.vornamen,
                               p_nachname    = p_analyst.nachname, 
                               p_email       = p_analyst.email,
                               p_start_datum = p_analyst.start_datum, 
                               p_ende_datum  = p_analyst.ende_datum
        )
    
    # Ref: UC-002 v0.1 – Laden aller Incident Analysts
    def get_all(self) -> list[IncidentAnalyst]:

        cursor = self._connection.cursor()

        cursor.execute(
            f'''
            SELECT id,
                vornamen,
                nachname,
                email,
                start_datum,
                ende_datum
            FROM {TABLE_NAME}
            ORDER BY nachname, vornamen
            '''
        )

        rows = cursor.fetchall()

        analysts = []

        for row in rows:
            analysts.append(
                IncidentAnalyst(
                    p_id=row[0],
                    p_vornamen=row[1],
                    p_nachname=row[2],
                    p_email=row[3],
                    p_start_datum=date.fromisoformat(row[4]),
                    p_ende_datum=date.fromisoformat(row[5]) if row[5] else None
                )
            )

        return analysts

    # Ref: UC-002 v0.1 – Löschen eines Incident Analysts
    def delete(self, p_id: int) -> None:

        cursor = self._connection.cursor()

        cursor.execute(
            f'''
            DELETE FROM {TABLE_NAME}
            WHERE id = ?
            ''',
            (p_id,)
        )

        self._connection.commit()