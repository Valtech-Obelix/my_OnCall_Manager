# CR-014 – Import-Dialog zeigt nächsten Importstart

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-02-28
- Umgesetzt am: 2026-02-28
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-005

## Beschreibung (fachlich)

Im Dialog „Import OpsGenie Shifts“ soll dem Benutzer angezeigt werden, ab
welchem Zeitpunkt neue Schichten eingelesen werden.

## Akzeptanzkriterien

- Für die aktuell gesetzte `Schedule ID` wird der nächste Importstart angezeigt.
- Bei Wechsel der Schichtplan-Auswahl oder Änderung der `Schedule ID` wird die
  Anzeige aktualisiert.
- Ist keine `Schedule ID` gesetzt, wird kein Zeitpunkt angezeigt.

## Technische Umsetzung

- Neue Service-Methode `get_next_import_start_local(schedule_id)` ergänzt.
- Neue Label-Zeile „Nächster Import ab:“ im Import-Dialog ergänzt.
- Anzeige wird bei Auswahländerung, Texteingabe und nach Import aktualisiert.

## Betroffene Dateien

- `src/services/opsgenie_service.py`
- `src/ui/opsgenie_import_dialog.py`
- `tests/test_opsgenie_service.py`
- `docs/use_cases/UC-005_Auswahl_Schichtplan.md`

## Tests / Validierung

- `PYTHONPATH=. .venv/bin/pytest -q tests/test_opsgenie_service.py`
- `python3 -m compileall src/services/opsgenie_service.py src/ui/opsgenie_import_dialog.py`
