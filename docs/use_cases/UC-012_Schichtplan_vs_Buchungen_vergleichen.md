# UC-012 – Schichtplan vs. Buchungen vergleichen

## Version
0.1

---

## Ziel

Als Administrator  
möchte ich geplante Schichten aus OpsGenie mit den gebuchten Schichten vergleichen können,  
um Abweichungen pro Woche schnell zu erkennen.

---

## Hauptablauf

1. Administrator öffnet den Dialog „Schichtplan vs. Buchungen vergleichen“.
2. Administrator wählt den Schichtplan.
3. Administrator wählt den Wochenstart (Montag bis Sonntag).
4. System zeigt links den Schichtplan laut OpsGenie.
5. System zeigt rechts die gebuchten Schichten aus den CSV-Dateien.
6. System markiert rechts korrekt gebuchte Schichten grün und abweichende rot.

---

## Akzeptanzkriterien

- Wochenbasierte Anzeige über auswählbares Startdatum.
- Linke Seite zeigt Soll-Daten (OpsGenie).
- Rechte Seite zeigt Ist-Daten (Buchungen, Tasktyp `On Call`).
- Farbmarkierung:
  - Grün: Soll und Ist stimmen überein
  - Rot: Abweichung
- Zuordnung der Schicht über Notes:
  - `früh`/`frueh`/`early`
  - `tag`/`day`
  - `spät`/`spaet`/`late`

## Zugehörige Change Requests

- [CR-020 – Vergleichsdialog Schichtplan vs. Buchungen (Wochenansicht)](../change_requests/CR-020_Vergleichsdialog_Schichtplan_vs_Buchungen.md)

