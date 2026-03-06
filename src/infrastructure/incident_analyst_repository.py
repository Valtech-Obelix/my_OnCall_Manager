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
                mitarbeitertyp,
                start_datum,
                ende_datum
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                p_analyst.vornamen,
                p_analyst.nachname,
                p_analyst.buchungsname,
                p_analyst.email,
                p_analyst.opsgenie_id,
                p_analyst.oncall_location_id,
                p_analyst.mitarbeitertyp,
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
                               p_mitarbeitertyp=p_analyst.mitarbeitertyp,
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
                mitarbeitertyp,
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
                    p_mitarbeitertyp=row[7],
                    p_start_datum=date.fromisoformat(row[8]),
                    p_ende_datum=date.fromisoformat(row[9]) if row[9] else None
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
                mitarbeitertyp,
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
            p_mitarbeitertyp=row[7],
            p_start_datum=date.fromisoformat(row[8]),
            p_ende_datum=date.fromisoformat(row[9]) if row[9] else None
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
                mitarbeitertyp,
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
            p_mitarbeitertyp=row[7],
            p_start_datum=date.fromisoformat(row[8]),
            p_ende_datum=date.fromisoformat(row[9]) if row[9] else None
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
                mitarbeitertyp,
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
            p_mitarbeitertyp=row[7],
            p_start_datum=date.fromisoformat(row[8]),
            p_ende_datum=date.fromisoformat(row[9]) if row[9] else None
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
                mitarbeitertyp = ?,
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
                p_analyst.mitarbeitertyp,
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

    def get_gehaltsgruppen_zuordnungen(
        self,
        p_mitarbeiter_id: int
    ) -> list[dict[str, str | int]]:
        cursor = self._connection.cursor()
        cursor.execute(
            '''
            SELECT
                mg.id,
                mg.gehaltsgruppe_id,
                g.bezeichnung,
                mg.gueltig_ab,
                mg.gueltig_bis
            FROM mitarbeiter_gehaltsgruppe mg
            JOIN gehaltsgruppe g ON g.id = mg.gehaltsgruppe_id
            WHERE mg.mitarbeiter_id = ?
            ORDER BY mg.gueltig_ab ASC
            ''',
            (int(p_mitarbeiter_id),)
        )
        rows = cursor.fetchall()
        return [
            {
                "id": int(row[0]),
                "gehaltsgruppe_id": int(row[1]),
                "gehaltsgruppe_bezeichnung": str(row[2]),
                "gueltig_ab": str(row[3]),
                "gueltig_bis": str(row[4]) if row[4] else "",
            }
            for row in rows
        ]

    def upsert_gehaltsgruppen_zuordnung(
        self,
        p_mitarbeiter_id: int,
        p_gehaltsgruppe_id: int,
        p_gueltig_ab: date,
        p_gueltig_bis: date | None,
    ) -> None:
        cursor = self._connection.cursor()
        gueltig_ab_text = p_gueltig_ab.isoformat()
        gueltig_bis_text = p_gueltig_bis.isoformat() if p_gueltig_bis else None

        cursor.execute(
            '''
            SELECT id
            FROM mitarbeiter_gehaltsgruppe
            WHERE mitarbeiter_id = ?
              AND gueltig_ab = ?
              AND (
                    (gueltig_bis IS NULL AND ? IS NULL)
                    OR gueltig_bis = ?
              )
            ''',
            (
                int(p_mitarbeiter_id),
                gueltig_ab_text,
                gueltig_bis_text,
                gueltig_bis_text,
            )
        )
        existing = cursor.fetchone()

        if existing is not None:
            cursor.execute(
                '''
                UPDATE mitarbeiter_gehaltsgruppe
                SET gehaltsgruppe_id = ?
                WHERE id = ?
                ''',
                (int(p_gehaltsgruppe_id), int(existing[0]))
            )
        else:
            cursor.execute(
                '''
                INSERT INTO mitarbeiter_gehaltsgruppe
                (mitarbeiter_id, gehaltsgruppe_id, gueltig_ab, gueltig_bis)
                VALUES (?, ?, ?, ?)
                ''',
                (
                    int(p_mitarbeiter_id),
                    int(p_gehaltsgruppe_id),
                    gueltig_ab_text,
                    gueltig_bis_text,
                )
            )
        self._connection.commit()

    def get_gehaltsgruppe_zuordnung_am_stichtag(
        self,
        p_mitarbeiter_id: int,
        p_stichtag: date
    ) -> dict[str, str | int] | None:
        cursor = self._connection.cursor()
        cursor.execute(
            '''
            SELECT
                mg.id,
                mg.gehaltsgruppe_id,
                g.bezeichnung,
                mg.gueltig_ab,
                mg.gueltig_bis
            FROM mitarbeiter_gehaltsgruppe mg
            JOIN gehaltsgruppe g ON g.id = mg.gehaltsgruppe_id
            WHERE mg.mitarbeiter_id = ?
              AND mg.gueltig_ab <= ?
              AND (mg.gueltig_bis IS NULL OR mg.gueltig_bis >= ?)
            ORDER BY mg.gueltig_ab DESC, mg.id DESC
            LIMIT 1
            ''',
            (int(p_mitarbeiter_id), p_stichtag.isoformat(), p_stichtag.isoformat())
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return {
            "id": int(row[0]),
            "gehaltsgruppe_id": int(row[1]),
            "gehaltsgruppe_bezeichnung": str(row[2]),
            "gueltig_ab": str(row[3]),
            "gueltig_bis": str(row[4]) if row[4] else "",
        }

    def update_gehaltsgruppen_zuordnung_end_date(
        self,
        p_assignment_id: int,
        p_gueltig_bis: date,
    ) -> None:
        cursor = self._connection.cursor()
        cursor.execute(
            '''
            UPDATE mitarbeiter_gehaltsgruppe
            SET gueltig_bis = ?
            WHERE id = ?
            ''',
            (p_gueltig_bis.isoformat(), int(p_assignment_id))
        )
        self._connection.commit()

    def get_activation_periods(self, p_mitarbeiter_id: int) -> list[dict[str, str | int]]:
        cursor = self._connection.cursor()
        cursor.execute(
            '''
            SELECT id, start_datum, ende_datum
            FROM mitarbeiter_aktivierung
            WHERE mitarbeiter_id = ?
            ORDER BY start_datum ASC, id ASC
            ''',
            (int(p_mitarbeiter_id),)
        )
        rows = cursor.fetchall()
        return [
            {
                "id": int(row[0]),
                "start_datum": str(row[1]),
                "ende_datum": str(row[2]) if row[2] else "",
            }
            for row in rows
        ]

    def get_open_activation_period(self, p_mitarbeiter_id: int) -> dict[str, str | int] | None:
        cursor = self._connection.cursor()
        cursor.execute(
            '''
            SELECT id, start_datum, ende_datum
            FROM mitarbeiter_aktivierung
            WHERE mitarbeiter_id = ?
              AND ende_datum IS NULL
            ORDER BY start_datum DESC, id DESC
            LIMIT 1
            ''',
            (int(p_mitarbeiter_id),)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return {
            "id": int(row[0]),
            "start_datum": str(row[1]),
            "ende_datum": str(row[2]) if row[2] else "",
        }

    def add_activation_period(
        self,
        p_mitarbeiter_id: int,
        p_start_datum: date,
        p_ende_datum: date | None = None,
    ) -> None:
        cursor = self._connection.cursor()
        cursor.execute(
            '''
            INSERT INTO mitarbeiter_aktivierung (mitarbeiter_id, start_datum, ende_datum)
            VALUES (?, ?, ?)
            ''',
            (
                int(p_mitarbeiter_id),
                p_start_datum.isoformat(),
                p_ende_datum.isoformat() if p_ende_datum else None,
            )
        )
        self._connection.commit()

    def close_activation_period(self, p_period_id: int, p_ende_datum: date) -> None:
        cursor = self._connection.cursor()
        cursor.execute(
            '''
            UPDATE mitarbeiter_aktivierung
            SET ende_datum = ?
            WHERE id = ?
            ''',
            (p_ende_datum.isoformat(), int(p_period_id))
        )
        self._connection.commit()

    def set_current_activation_window(
        self,
        p_mitarbeiter_id: int,
        p_start_datum: date,
        p_ende_datum: date | None = None,
    ) -> None:
        cursor = self._connection.cursor()
        cursor.execute(
            '''
            UPDATE incident_analyst
            SET start_datum = ?, ende_datum = ?
            WHERE id = ?
            ''',
            (
                p_start_datum.isoformat(),
                p_ende_datum.isoformat() if p_ende_datum else None,
                int(p_mitarbeiter_id),
            )
        )
        self._connection.commit()
