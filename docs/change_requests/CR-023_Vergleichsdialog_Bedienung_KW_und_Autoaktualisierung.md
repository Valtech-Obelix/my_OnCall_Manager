# CR-023 – Vergleichsdialog: Kalenderwoche, Autoaktualisierung und Schließen-Button

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-03-05
- Umgesetzt am: 2026-03-05
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-016, UC-012

## Beschreibung (fachlich)

Die Bedienung des Vergleichsdialogs soll vereinfacht werden:
kein separater „Vergleich anzeigen“-Button, stattdessen automatische Aktualisierung
bei Parameteränderungen sowie Auswahl über Kalenderwoche.

## Akzeptanzkriterien

- Eingabe über `Jahr` + `Kalenderwoche` statt Wochenstart-Datum.
- Vergleich aktualisiert automatisch bei Änderung von Schichtplan, Jahr, KW oder IA-Filter.
- Unterhalb der Tabellen ist rechts ein Button `Dialog schließen`.
- Der frühere Button `Vergleich anzeigen` entfällt.

## Technische Umsetzung

- `QDateEdit` durch `QSpinBox` für Jahr/KW ersetzt.
- ISO-Woche wird intern per `date.fromisocalendar(year, week, 1)` berechnet.
- Refresh-Trigger an alle relevanten Auswahlfelder gebunden.
- Unten rechts Closing-Button ergänzt.

## Betroffene Dateien

- `src/ui/shift_booking_compare_dialog.py`

## Tests / Validierung

- `python -m py_compile src/ui/shift_booking_compare_dialog.py`

