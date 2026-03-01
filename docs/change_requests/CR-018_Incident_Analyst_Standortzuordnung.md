# CR-018 – Incident-Analysten einem Rufbereitschaftsstandort zuordnen (Option 1)

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-03-01
- Umgesetzt am: 2026-03-01
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-011

## Beschreibung (fachlich)

Incident-Analysten sollen genau einem Rufbereitschaftsstandort zugeordnet werden können
(Option 1: 1 Standort pro IA).  
Bei der Erweiterung der bestehenden Daten muss für bereits vorhandene Incident-Analysten
automatisch `GER` gesetzt werden.

## Akzeptanzkriterien

- `incident_analyst` enthält ein neues Pflichtfeld `oncall_location_id`.
- Das Feld hat genau 3 Zeichen und verweist fachlich auf einen Rufbereitschaftsstandort.
- Bestehende IA-Datensätze werden bei Migration mit `GER` vorbelegt.
- Beim Anlegen/Bearbeiten eines IA ist der Standort auswählbar.
- Standardwert ist `GER`.

## Technische Umsetzung

- Schema erweitert um `incident_analyst.oncall_location_id` mit Default `GER`.
- Migrationslogik ergänzt, damit bestehende Datensätze auf `GER` gesetzt werden.
- Default-Standort `GER` (`Deutschland`) wird im Standortstamm sichergestellt.
- Domain-Entity `IncidentAnalyst` um `oncall_location_id` erweitert inkl. Validierung.
- Repository/Service/Application um das neue Feld erweitert (lesen, anlegen, ändern).
- IA-Dialoge (Neu/Bearbeiten) um Standort-Auswahl ergänzt.

## Betroffene Dateien

- `src/domain/incident_analyst.py`
- `src/infrastructure/database.py`
- `src/infrastructure/incident_analyst_repository.py`
- `src/services/incident_analyst_service.py`
- `src/app/application.py`
- `src/ui/incident_analyst_add_dialog.py`
- `src/ui/incident_analyst_edit_dialog.py`
- `tests/test_incident_analyst.py`
- `tests/test_incident_analyst_repository.py`
- `tests/test_incident_analyst_service.py`
- `tests/test_database_schema.py`

## Tests / Validierung

- `python3 -m compileall src tests`
- `python3 -m pytest -q tests/test_incident_analyst.py tests/test_incident_analyst_repository.py tests/test_incident_analyst_service.py tests/test_database_schema.py`

