# CR-001 – Feldbezeichnung auf „Name des Schichtplans“ ändern

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-02-27
- Umgesetzt am: 2026-02-27
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-005

## Beschreibung (fachlich)

Das Eingabefeld im OpsGenie-Importdialog soll nicht mehr „Projekt“, sondern „Name des Schichtplans“ heißen.

## Akzeptanzkriterien

- Im Dialog ist die Feldbezeichnung „Name des Schichtplans“ sichtbar.
- Die Eingabe wird für Import und Historie genutzt.

## Technische Umsetzung

- Umbenennung im UI von `project` auf `schedule_name`.
- Übergabeparameter im Service für den Import entsprechend angepasst.

## Betroffene Dateien

- `src/ui/opsgenie_import_dialog.py`
- `src/services/opsgenie_service.py`
- `src/infrastructure/shift_repository.py`

## Tests / Validierung

- `python3 -m compileall src tests`
- `.venv/bin/python -m pytest -q`
