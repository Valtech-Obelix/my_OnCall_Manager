# CR-034 – Legacy-Tabellen bereinigen

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-03-05
- Umgesetzt am: 2026-03-05
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-019

## Beschreibung (fachlich)

Nicht mehr verwendete Legacy-Tabellen und Legacy-Spalten in der App-Datenbank fuehren zu
Verwirrung bei der Datenanalyse und Pflege.

## Akzeptanzkriterien

- Veraltete Legacy-Tabellen werden beim Schema-Init entfernt.
- Legacy-Spalten in `incident_analyst` werden entfernt.
- Fachlich aktuelle Tabellenstruktur bleibt unveraendert funktionsfaehig.

## Technische Umsetzung

- `initialize_schema()` erweitert um `DROP TABLE IF EXISTS` fuer:
  - `salary_group_rate`
  - `employee_salary_group_assignment`
  - `salary_group`
  - `budget_cost_rate`
  - `budget_source`
- `incident_analyst` wird bei Legacy-Bestand auf das aktuelle Zielschema
  ohne `gehaltsgruppe` und `mitarbeiter_typ` migriert.

## Betroffene Dateien

- `src/infrastructure/database.py`
- `docs/change_requests/00_CR_Index.md`

## Tests / Validierung

- `PYTHONPATH=. .venv/bin/pytest -q tests/test_database_schema.py`
