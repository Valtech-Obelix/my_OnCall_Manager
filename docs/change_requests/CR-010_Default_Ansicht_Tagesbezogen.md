# CR-010 – Default-Ansicht auf „Tagesbezogen“ setzen

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-02-28
- Umgesetzt am: 2026-02-28
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-008

## Beschreibung (fachlich)

Beim Öffnen des Dialogs „Schichtplan anzeigen“ soll die Darstellungsart
standardmäßig auf `Tagesbezogen` stehen statt auf `Schichtbezogen`.

## Akzeptanzkriterien

- Nach dem Öffnen des Dialogs ist `Tagesbezogen` vorausgewählt.
- Die Darstellung wird initial in der tagesbezogenen Tabellenstruktur aufgebaut.

## Technische Umsetzung

- Default der ComboBox `Ansicht` auf `Tagesbezogen` gesetzt.

## Betroffene Dateien

- `src/ui/shift_plan_view_dialog.py`

## Tests / Validierung

- `python3 -m compileall src/ui/shift_plan_view_dialog.py`
