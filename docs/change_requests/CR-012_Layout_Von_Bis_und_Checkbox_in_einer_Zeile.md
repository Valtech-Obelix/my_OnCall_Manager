# CR-012 – Layout: Von/Bis und Checkbox in einer Zeile

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-02-28
- Umgesetzt am: 2026-02-28
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-008

## Beschreibung (fachlich)

Im Dialog „Schichtplan anzeigen“ soll das `Bis`-Datum direkt neben dem
`Von`-Datum erscheinen.  
Die Checkbox für den Gesamtzeitraum soll rechts davon im selben Bereich
angeordnet sein.

## Akzeptanzkriterien

- `Von` und `Bis` sind horizontal nebeneinander platziert.
- Die Checkbox steht rechts hinter den beiden Datumsfeldern.

## Technische Umsetzung

- Separate Zeilen (`Von`, `Bis`, Checkbox) durch eine gemeinsame
  horizontale Zeitraum-Zeile ersetzt.

## Betroffene Dateien

- `src/ui/shift_plan_view_dialog.py`

## Tests / Validierung

- `python3 -m compileall src/ui/shift_plan_view_dialog.py`
