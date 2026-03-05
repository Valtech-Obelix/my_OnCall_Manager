# CR-024 – Gegenbuchungen netto verrechnen (Vergleich und Monatsabrechnung)

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-03-05
- Umgesetzt am: 2026-03-05
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-016, UC-015

## Beschreibung (fachlich)

Buchungen mit negativen Stundenwerten (`Time (Hours)`, z. B. `-1`) sind Gegenbuchungen
und müssen zugehörige Fehl-/Doppelbuchungen neutralisieren.
Die Nettoverrechnung muss sowohl im Soll/Ist-Vergleich als auch in der Auszahlung gelten.

## Akzeptanzkriterien

- CSV-Buchungen werden über `Time (Hours)` netto aggregiert.
- `+1` und `-1` auf gleicher Buchungsdimension heben sich auf.
- Nur Netto-Positivwerte fließen in Vergleich und Auszahlung ein.
- Verhalten ist konsistent in Vergleichsdialog und Monatsabrechnung.

## Technische Umsetzung

- Parsing für Stundenwerte (`Decimal`) ergänzt.
- On-Call-Buchungen vor Weiterverarbeitung netto aggregiert.
- Vergleichsdialog nutzt dieselbe Netto-Logik für Zählung und Validierung.
- Monatsabrechnung verarbeitet nur netto wirksame Buchungen.

## Betroffene Dateien

- `src/services/compensation_service.py`
- `src/ui/shift_booking_compare_dialog.py`
- `tests/test_compensation_service.py`

## Tests / Validierung

- `pytest tests/test_compensation_service.py`

