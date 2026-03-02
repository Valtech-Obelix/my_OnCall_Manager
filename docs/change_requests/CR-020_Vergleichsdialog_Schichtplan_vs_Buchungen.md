# CR-020 – Vergleichsdialog Schichtplan vs. Buchungen (Wochenansicht)

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-03-01
- Umgesetzt am: 2026-03-01
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-012

## Beschreibung (fachlich)

Für den Abgleich zwischen Planung und Erfassung wird ein Dialog benötigt, in dem
eine Woche über ein Startdatum ausgewählt werden kann.  
Links werden die geplanten Schichten aus OpsGenie angezeigt, rechts die gebuchten
Schichten aus den CSV-Dateien.  
Korrekte Buchungen sollen grün, abweichende Buchungen rot visualisiert werden.

## Akzeptanzkriterien

- Auswahl von `Schichtplan` und `Wochenstart` ist möglich.
- Linke Tabelle zeigt die geplanten Schichten (Datum, Schicht, Mitarbeiter).
- Rechte Tabelle zeigt die gebuchten Schichten (Datum, Schicht, Mitarbeiter).
- Rechte Tabelle wird pro Zeile farblich markiert:
  - Grün bei exakter Übereinstimmung
  - Rot bei Abweichung
- Berücksichtigt werden nur CSV-Buchungen mit `Task - Task type = On Call`.
- Schichtzuordnung aus `Notes` über deutsch/englisch:
  - `früh/frueh/early`, `tag/day`, `spät/spaet/late`.

## Technische Umsetzung

- Neuer Dialog `ShiftBookingCompareDialog`.
- Neuer Menüeintrag unter `Auswertung`.
- Einlesen aller `data/*.csv` mit Header-Erkennung.
- Wochenfilter auf Montag-Sonntag basierend auf gewähltem Startdatum.
- Vergleich auf Schlüssel `Datum + Schicht`.
- Mitarbeitervergleich als Mengen-/Anzahlvergleich (inkl. Duplikaterkennung).

## Betroffene Dateien

- `src/ui/shift_booking_compare_dialog.py`
- `src/ui/main_window.py`
- `docs/use_cases/UC-012_Schichtplan_vs_Buchungen_vergleichen.md`

## Tests / Validierung

- `python3 -m compileall -q src`

