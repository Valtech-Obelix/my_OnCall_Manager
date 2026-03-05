# CR-028 – Mitarbeitertyp im Mitarbeiterdialog und Datenmodell

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-03-05
- Umgesetzt am: 2026-03-05
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-018

## Beschreibung (fachlich)

Die bestehende Incident-Analyst-Verwaltung wird zu einer allgemeinen
Mitarbeiterverwaltung erweitert. Hierfuer wird ein neues Attribut
`mitarbeitertyp` eingefuehrt, damit neben Incident Analysts auch
Product Owner und sonstige Mitarbeiter gepflegt werden koennen.

## Akzeptanzkriterien

- Neues Attribut `mitarbeitertyp` ist im Datenmodell vorhanden.
- Bestehende Datensaetze werden bei Migration mit `INCIDENT_ANALYST` vorbelegt.
- UI bietet Auswahl fuer `Mitarbeitertyp`.
- Menuepunkt und Dialogtitel sind auf `Mitarbeiter` angepasst.

## Technische Umsetzung

- Tabelle `incident_analyst` um Spalte `mitarbeitertyp` erweitert inkl. CHECK-Constraint.
- Schema-Migration fuer Bestandsdaten hinzugefuegt.
- Domain, Repository und Service um `mitarbeitertyp` erweitert.
- Mitarbeiterdialog um Typauswahl und Typspalte ergaenzt.
- Menuebezeichnung in der Hauptnavigation angepasst.

## Betroffene Dateien

- `src/infrastructure/database.py`
- `src/domain/incident_analyst.py`
- `src/infrastructure/incident_analyst_repository.py`
- `src/services/incident_analyst_service.py`
- `src/app/application.py`
- `src/ui/incident_analyst_dialog.py`
- `src/ui/main_window.py`
- `tests/test_database_schema.py`
- `tests/test_incident_analyst.py`
- `tests/test_incident_analyst_repository.py`
- `tests/test_incident_analyst_service.py`
- `docs/use_cases/UC-018_Einfuehrung_von_Mitarbeitertypen.md`

## Tests / Validierung

- `PYTHONPATH=. .venv/bin/pytest -q tests/test_database_schema.py tests/test_incident_analyst.py tests/test_incident_analyst_repository.py tests/test_incident_analyst_service.py`
