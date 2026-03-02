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
            (
                vornamen,
                nachname,
                buchungsname,
                email,
                opsgenie_id,
                oncall_location_id,
                start_datum,
                ende_datum
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                p_analyst.vornamen,
                p_analyst.nachname,
                p_analyst.buchungsname,
                p_analyst.email,
                p_analyst.opsgenie_id,
                p_analyst.oncall_location_id,
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
                               p_buchungsname= p_analyst.buchungsname,
                               p_email       = p_analyst.email,
                               p_opsgenie_id = p_analyst.opsgenie_id,
                               p_oncall_location_id=p_analyst.oncall_location_id,
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
                buchungsname,
                email,
                opsgenie_id,
                oncall_location_id,
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
                    p_buchungsname=row[3],
                    p_email=row[4],
                    p_opsgenie_id=row[5],
                    p_oncall_location_id=row[6],
                    p_start_datum=date.fromisoformat(row[7]),
                    p_ende_datum=date.fromisoformat(row[8]) if row[8] else None
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

    # Ref: UC-003 – Enddatum setzen
    def update_end_date(self, p_id: int, p_ende_datum):

        cursor = self._connection.cursor()

        cursor.execute(
            f'''
            UPDATE {TABLE_NAME}
            SET ende_datum = ?
            WHERE id = ?
            ''',
            (p_ende_datum.isoformat(), p_id)
        )

        self._connection.commit()
        
    # UC-004
    def find_by_email(self, p_email: str) -> IncidentAnalyst | None:

        cursor = self._connection.cursor()

        cursor.execute(
            '''
            SELECT id,
                vornamen,
                nachname,
                buchungsname,
                email,
                opsgenie_id,
                oncall_location_id,
                start_datum,
                ende_datum
            FROM incident_analyst
            WHERE lower(email) = lower(?)
            ''',
            (p_email,)
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return IncidentAnalyst(
            p_id=row[0],
            p_vornamen=row[1],
            p_nachname=row[2],
            p_buchungsname=row[3],
            p_email=row[4],
            p_opsgenie_id=row[5],
            p_oncall_location_id=row[6],
            p_start_datum=date.fromisoformat(row[7]),
            p_ende_datum=date.fromisoformat(row[8]) if row[8] else None
        )

    # UC-004 / CR-008
    def find_by_opsgenie_id(self, p_opsgenie_id: str) -> IncidentAnalyst | None:
        cursor = self._connection.cursor()
        cursor.execute(
            '''
            SELECT id,
                vornamen,
                nachname,
                buchungsname,
                email,
                opsgenie_id,
                oncall_location_id,
                start_datum,
                ende_datum
            FROM incident_analyst
            WHERE lower(opsgenie_id) = lower(?)
            ''',
            (p_opsgenie_id,)
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return IncidentAnalyst(
            p_id=row[0],
            p_vornamen=row[1],
            p_nachname=row[2],
            p_buchungsname=row[3],
            p_email=row[4],
            p_opsgenie_id=row[5],
            p_oncall_location_id=row[6],
            p_start_datum=date.fromisoformat(row[7]),
            p_ende_datum=date.fromisoformat(row[8]) if row[8] else None
        )

    def find_by_id(self, p_id: int) -> IncidentAnalyst | None:
        cursor = self._connection.cursor()
        cursor.execute(
            f'''
            SELECT id,
                vornamen,
                nachname,
                buchungsname,
                email,
                opsgenie_id,
                oncall_location_id,
                start_datum,
                ende_datum
            FROM {TABLE_NAME}
            WHERE id = ?
            ''',
            (p_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return IncidentAnalyst(
            p_id=row[0],
            p_vornamen=row[1],
            p_nachname=row[2],
            p_buchungsname=row[3],
            p_email=row[4],
            p_opsgenie_id=row[5],
            p_oncall_location_id=row[6],
            p_start_datum=date.fromisoformat(row[7]),
            p_ende_datum=date.fromisoformat(row[8]) if row[8] else None
        )

    def update(self, p_analyst: IncidentAnalyst) -> IncidentAnalyst:
        cursor = self._connection.cursor()
        cursor.execute(
            f'''
            UPDATE {TABLE_NAME}
            SET vornamen = ?,
                nachname = ?,
                buchungsname = ?,
                email = ?,
                opsgenie_id = ?,
                oncall_location_id = ?,
                start_datum = ?,
                ende_datum = ?
            WHERE id = ?
            ''',
            (
                p_analyst.vornamen,
                p_analyst.nachname,
                p_analyst.buchungsname,
                p_analyst.email,
                p_analyst.opsgenie_id,
                p_analyst.oncall_location_id,
                p_analyst.start_datum.isoformat(),
                p_analyst.ende_datum.isoformat()
                if p_analyst.ende_datum
                else None,
                p_analyst.id
            )
        )
        self._connection.commit()
        return p_analyst

    def update_opsgenie_id(self, p_id: int, p_opsgenie_id: str) -> None:
        cursor = self._connection.cursor()
        cursor.execute(
            f'''
            UPDATE {TABLE_NAME}
            SET opsgenie_id = ?
            WHERE id = ?
            ''',
            (p_opsgenie_id, p_id)
        )
        self._connection.commit()
