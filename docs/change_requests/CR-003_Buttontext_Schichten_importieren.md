# CR-003 – Import-Button umbenennen

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-02-27
- Umgesetzt am: 2026-02-27
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-005

## Beschreibung (fachlich)

Der Button „Import“ soll in „Schichten importieren“ umbenannt werden.

## Akzeptanzkriterien

- Der primäre Aktionsbutton trägt den Text „Schichten importieren“.

## Technische Umsetzung

- Beschriftung des Import-Buttons im OpsGenie-Dialog angepasst.

## Betroffene Dateien

- `src/ui/opsgenie_import_dialog.py`

## Tests / Validierung

- `python3 -m compileall src tests`
- `.venv/bin/python -m pytest -q`
