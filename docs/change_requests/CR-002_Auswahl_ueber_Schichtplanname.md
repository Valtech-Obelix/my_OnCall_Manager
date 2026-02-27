# CR-002 – Auswahl über Namen des Schichtplans

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-02-27
- Umgesetzt am: 2026-02-27
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-005

## Beschreibung (fachlich)

Die Auswahl bereits bekannter Schichtpläne soll primär über den Namen des Schichtplans erfolgen.

## Akzeptanzkriterien

- Die Historie wird im Dialog über den Schichtplannamen angezeigt.
- Bei Auswahl eines Namens wird die zugehörige Schedule-ID automatisch gesetzt.
- Der zuletzt genutzte Schichtplan ist beim Öffnen vorausgewählt.

## Technische Umsetzung

- Historieneinträge auf `schedule_name` umgestellt.
- Rückwärtskompatibler Fallback für ältere Historieneinträge ohne Namen beibehalten.
- UI-Logik auf Namensauswahl umgestellt.

## Betroffene Dateien

- `src/ui/opsgenie_import_dialog.py`
- `src/services/opsgenie_service.py`
- `src/infrastructure/shift_repository.py`
- `tests/test_shift_repository.py`

## Tests / Validierung

- `python3 -m compileall src tests`
- `.venv/bin/python -m pytest -q`
