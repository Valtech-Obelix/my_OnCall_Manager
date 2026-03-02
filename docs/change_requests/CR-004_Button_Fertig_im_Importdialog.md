# CR-004 – Button „Fertig“ im Import-Dialog ergänzen

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-02-27
- Umgesetzt am: 2026-02-27
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-005

## Beschreibung (fachlich)

Neben dem Import-Button soll ein zusätzlicher Button „Fertig“ bereitstehen, mit dem der Benutzer den Dialog schließen kann.

## Akzeptanzkriterien

- Im Dialog sind zwei Buttons sichtbar: „Schichten importieren“ und „Fertig“.
- „Fertig“ schließt den Dialog ohne Import.

## Technische Umsetzung

- Zweiten Button im Button-Layout ergänzt.
- Callback auf `reject()` gesetzt.

## Betroffene Dateien

- `src/ui/opsgenie_import_dialog.py`

## Tests / Validierung

- `python3 -m compileall src tests`
- `.venv/bin/python -m pytest -q`
