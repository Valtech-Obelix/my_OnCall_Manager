# UC-008 – Schichtplan anzeigen

## Ziel
Als Administrator  
möchte ich mir einen Schichtplan anzeigen lassen können  
um diesen mit den Buchungen vergleichen zu können.

## Modul-Zuordnung
- UI: `main_window.py`, `shift_plan_view_dialog.py`
- Geschäftslogik: `application.py`
- Datenhaltung: `shift_repository.py`

## Akteur
Administrator

## Vorbedingungen
- Es sind Schichten zu mindestens einem Schichtplan importiert.

## Trigger
- Auswahl „Schichtplan anzeigen“ im Hauptmenü.

## Hauptablauf
1. Administrator öffnet den Dialog „Schichtplan anzeigen“.
2. Administrator wählt einen Schichtplan aus.
3. Administrator wählt die Darstellungsart:
   - schichtbezogen (eine Schicht pro Zeile)
   - tagesbezogen (eine Zeile pro Tag, bis zu drei Schichteinträge)
4. System lädt standardmäßig den gesamten verfügbaren Zeitraum.
5. Optional deaktiviert Administrator „gesamter Zeitraum“ und setzt `Von/Bis`.
6. Administrator klickt auf „Anzeigen“.
7. System zeigt die Daten entsprechend der Auswahl an.

## Akzeptanzkriterien
- Schichtplan ist auswählbar und anzeigbar.
- Schichtbezogene Ansicht zeigt pro Schicht genau eine Zeile.
- Tagesbezogene Ansicht zeigt pro Tag genau eine Zeile mit drei Schicht-Spalten.
- Zeitraum ist per Datum steuerbar.
- Default ist immer der gesamte verfügbare Zeitraum des gewählten Schichtplans.

## Status
abgeschlossen

## Version
0.1
