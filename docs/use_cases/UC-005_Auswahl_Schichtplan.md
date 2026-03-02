# UC-005 – Auswahl Schichtplan

## Version
0.3

---

## Ziel

Als Administrator  
möchte ich die Kennung nur einmal beim ersten Abruf der Schichten eingeben. Bei jedem nachfolgendem Abruf
möchte ich den Schichtplan aus der Liste der bisher abgerufenen Schichtpläne auswählen können,
um ausschließlich fachlich relevante On-Call-Zeiträume der Incident-Analysten auszuwerten.

---

## Hauptablauf

1. Administrator öffnet den Import-Dialog.
2. System lädt die Historie der bereits importierten Schichtpläne.
3. Administrator wählt einen vorhandenen Schichtplan über den Namen des Schichtplans aus
   oder erfasst einen neuen Namen.
4. System setzt bei Auswahl automatisch die zugehörige `Schedule ID`.
5. System zeigt „Nächster Import ab“ für die aktuell gesetzte `Schedule ID`.
6. Administrator startet den Import über „Schichten importieren“ oder beendet den Dialog über „Fertig“.

---

## Akzeptanzkriterien

- Feldbezeichnung lautet „Name des Schichtplans“.
- Auswahl erfolgt primär über den Namen des Schichtplans.
- Zu ausgewähltem Namen wird die passende `Schedule ID` vorbelegt.
- Für die aktuelle `Schedule ID` wird der nächste Importstart angezeigt.
- Letzter verwendeter Schichtplan ist beim Öffnen vorausgewählt.
- Buttontexte lauten „Schichten importieren“ und „Fertig“.

## Zugehörige Change Requests

- [CR-001 – Feldbezeichnung auf „Name des Schichtplans“ ändern](../change_requests/CR-001_Feldbezeichnung_Schichtplanname.md)
- [CR-002 – Auswahl über Namen des Schichtplans](../change_requests/CR-002_Auswahl_ueber_Schichtplanname.md)
- [CR-003 – Import-Button umbenennen](../change_requests/CR-003_Buttontext_Schichten_importieren.md)
- [CR-004 – Button „Fertig“ im Import-Dialog ergänzen](../change_requests/CR-004_Button_Fertig_im_Importdialog.md)
- [CR-005 – Schichtplan-Referenzen unabhängig persistieren](../change_requests/CR-005_Unabhaengige_Persistenz_Schichtplanreferenzen.md)
- [CR-014 – Import-Dialog zeigt nächsten Importstart](../change_requests/CR-014_Importdialog_zeigt_naechsten_Importstart.md)
