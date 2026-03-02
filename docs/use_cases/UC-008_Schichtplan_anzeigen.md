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
4. System lädt standardmäßig die tagesbezogene Ansicht.
5. System setzt standardmäßig den Zeitraum von Montag vor zwei Wochen bis zum Vortag.
6. Optional aktiviert Administrator „gesamter Zeitraum“.
7. Administrator klickt auf „Anzeige aktualisieren“.
8. System zeigt die Daten entsprechend der Auswahl an.

## Akzeptanzkriterien
- Schichtplan ist auswählbar und anzeigbar.
- Schichtbezogene Ansicht zeigt pro Schicht genau eine Zeile.
- Tagesbezogene Ansicht zeigt pro Tag genau eine Zeile mit drei Schicht-Spalten.
- Zeitraum ist per Datum steuerbar.
- Default-Ansicht ist tagesbezogen.
- Default-Zeitraum ist Montag vor zwei Wochen bis Vortag.
- Button „Anzeige aktualisieren“ ist nur aktiv, wenn Parameter geändert wurden.

## Status
abgeschlossen

## Version
0.2

## Zugehörige Change Requests
- [CR-010 – Default-Ansicht auf „Tagesbezogen“ setzen](../change_requests/CR-010_Default_Ansicht_Tagesbezogen.md)
- [CR-011 – Default-Zeitraum: letzte 2 Wochen (Mo-So) bis Vortag](../change_requests/CR-011_Default_Zeitraum_Letzte_2_Wochen_bis_Vortag.md)
- [CR-012 – Layout: Von/Bis und Checkbox in einer Zeile](../change_requests/CR-012_Layout_Von_Bis_und_Checkbox_in_einer_Zeile.md)
- [CR-013 – Button „Anzeige aktualisieren“ mit Dirty-State](../change_requests/CR-013_Button_Anzeige_aktualisieren_mit_Dirty_State.md)
