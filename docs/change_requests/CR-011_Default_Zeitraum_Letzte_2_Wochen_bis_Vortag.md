# CR-011 – Default-Zeitraum: letzte 2 Wochen (Mo-So) bis Vortag

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-02-28
- Umgesetzt am: 2026-02-28
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-008

## Beschreibung (fachlich)

Die Vorbelegung des Zeitraums im Dialog „Schichtplan anzeigen“ soll nicht
mehr den gesamten verfügbaren Zeitraum verwenden.  
Stattdessen soll die Auswahl standardmäßig von Montag vor zwei Wochen bis
zum Vortag reichen.

## Akzeptanzkriterien

- Checkbox „Gesamten verfügbaren Zeitraum anzeigen“ ist initial deaktiviert.
- `Von` ist standardmäßig der Montag von vor zwei Wochen.
- `Bis` ist standardmäßig der Vortag.
- Falls der gewünschte Default außerhalb der verfügbaren Schichten liegt,
  wird auf den tatsächlich verfügbaren Bereich begrenzt.

## Technische Umsetzung

- Neue Default-Berechnung im Dialog:
  - `start = heute - (weekday + 14 Tage)`
  - `end = heute - 1 Tag`
- Begrenzung auf die im gewählten Schedule vorhandenen Daten.

## Betroffene Dateien

- `src/ui/shift_plan_view_dialog.py`

## Tests / Validierung

- `python3 -m compileall src/ui/shift_plan_view_dialog.py`
