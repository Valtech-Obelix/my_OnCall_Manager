# CR-007 – Tabelle `incident_analyst` um `opsgenie_id` erweitern

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-02-28
- Umgesetzt am: 2026-02-28
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-001

## Beschreibung (fachlich)

Die Tabelle `incident_analyst` soll um eine optionale Spalte `opsgenie_id` erweitert werden.  
Bestehende Daten müssen bei der Schema-Erweiterung vollständig erhalten bleiben.

## Akzeptanzkriterien

- Die Tabelle `incident_analyst` enthält die neue Spalte `opsgenie_id`.
- Bereits vorhandene Incident-Analyst-Datensätze bleiben bei der Erweiterung erhalten.
- Die Schema-Initialisierung ist für Neuinstallation und Bestandsdatenbank lauffähig.

## Technische Umsetzung

- `CREATE TABLE`-Definition um `opsgenie_id TEXT` ergänzt.
- Migrationssichere Nachrüstung ergänzt:
  `PRAGMA table_info(incident_analyst)` prüft den Spaltenbestand, bei Bedarf erfolgt
  `ALTER TABLE incident_analyst ADD COLUMN opsgenie_id TEXT`.
- Integrationstest ergänzt, der Datenbestand vor/nach Migration validiert.

## Betroffene Dateien

- `src/infrastructure/database.py`
- `tests/test_database_schema.py`

## Tests / Validierung

- `python3 -m compileall src tests`
- `.venv/bin/python -m pytest -q`
