# CR-006 – Logging übersprungener Schichtplan-Einträge mit JSON-Ausschnitt

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-02-28
- Umgesetzt am: 2026-02-28
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-004

## Beschreibung (fachlich)

Beim Import sollen im Log-File übersprungene Schichtplan-Einträge nachvollziehbar sein.  
Dafür soll pro übersprungenem Eintrag der Grund im Warning-Log stehen und der zugehörige relevante Abschnitt aus dem JSON-Content im Debug-Log stehen.  
Zusätzlich soll der vollständige JSON-Content bei Bedarf über eine Checkbox in eine separate Datei für den letzten Import geschrieben werden.

## Akzeptanzkriterien

- Für jeden übersprungenen Schichtplan-Eintrag wird ein Warning-Log erzeugt.
- Für jeden übersprungenen Schichtplan-Eintrag wird zusätzlich ein Debug-Log mit JSON-Ausschnitt erzeugt.
- Der vollständige RAW-JSON-Response wird nicht mehr geloggt.
- Über eine Checkbox kann optional ein vollständiger JSON-Dump des letzten Imports geschrieben werden.

## Technische Umsetzung

- Vollständiges RAW-JSON-Debug-Logging aus dem OpsGenie-Import entfernt.
- Zentrale Helper-Methode für Skip-Logs ergänzt (Warning ohne Snippet, Debug mit Snippet).
- In allen Skip-Pfaden (`recipient` fehlt, `recipient.type != user`, Email fehlt, Analyst nicht gefunden, Duplikat) werden Warning- und Debug-Logeinträge geschrieben.
- Checkbox im Import-Dialog ergänzt und an den Service durchgereicht.
- Optionales Schreiben des vollständigen JSON-Dumps nach `debug/last_opsgenie_import.json` (wird pro Import überschrieben).
- Tests für das neue Logging- und Dump-Verhalten ergänzt.

## Betroffene Dateien

- `src/services/opsgenie_service.py`
- `src/ui/opsgenie_import_dialog.py`
- `tests/test_opsgenie_service.py`
- `docs/use_cases/UC-004_Aktuellen_Schichtplan_aus_Opsgenie_lesen`

## Tests / Validierung

- `python3 -m compileall src tests`
- `.venv/bin/python -m pytest -q`
