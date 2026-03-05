# CR-030 – Buchungsname als `Nachname, Vorname`

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-03-05
- Umgesetzt am: 2026-03-05
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-001, UC-018

## Beschreibung (fachlich)

Beim Anlegen neuer Mitarbeiter wurde der Buchungsname fehlerhaft als
`Vorname Nachname` erzeugt. Korrekt ist das Format `Nachname, Vorname`.

## Akzeptanzkriterien

- Bei Neuanlage wird der Buchungsname automatisch als `Nachname, Vorname` generiert.
- Bestehende manuell gesetzte Buchungsnamen bleiben unveraendert.

## Technische Umsetzung

- Ableitungsregel in der Domain-Entity `IncidentAnalyst` angepasst.
- Betroffene Tests auf neues Sollformat aktualisiert.

## Betroffene Dateien

- `src/domain/incident_analyst.py`
- `tests/test_incident_analyst.py`
- `tests/test_incident_analyst_repository.py`
- `docs/change_requests/00_CR_Index.md`

## Tests / Validierung

- `PYTHONPATH=. .venv/bin/pytest -q tests/test_incident_analyst.py tests/test_incident_analyst_repository.py`
