# CR-025 – Einheitliche Buttonleiste mit „Dialog schließen“

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-03-05
- Umgesetzt am: 2026-03-05
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-001, UC-005, UC-008, UC-009, UC-011, UC-012, UC-013, UC-015

## Beschreibung (fachlich)

Alle Dialoge sollen einheitlich eine untere Buttonleiste mit dem Button
`Dialog schließen` bereitstellen.

## Akzeptanzkriterien

- In allen relevanten Dialogen ist unten ein `Dialog schließen`-Button vorhanden.
- Benennung ist konsistent (`Dialog schließen`).
- Button beendet den Dialog zuverlässig.

## Technische Umsetzung

- Fehlende Close-Leisten ergänzt.
- Bestehende Buttons `Schließen`/`Fertig` auf `Dialog schließen` vereinheitlicht.
- Close-Handler in Dialogen auf einheitliches Verhalten angepasst.

## Betroffene Dateien

- `src/ui/shift_plan_view_dialog.py`
- `src/ui/incident_analyst_shift_count_dialog.py`
- `src/ui/location_shift_distribution_dialog.py`
- `src/ui/monthly_compensation_dialog.py`
- `src/ui/opsgenie_import_dialog.py`
- `src/ui/oncall_location_dialog.py`
- `src/ui/incident_analyst_dialog.py`

## Tests / Validierung

- `python -m py_compile src/ui/*.py`

