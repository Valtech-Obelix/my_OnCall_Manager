# CR-026 – Monatsabrechnung: Überstunden nach Task und Standort ausweisen

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-03-05
- Umgesetzt am: 2026-03-05
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-015

## Beschreibung (fachlich)

Im Dialog „Monatsabrechnung IA-Auszahlung“ sollen neben On-Call-Schichten auch
Überstunden sichtbar sein. Die Überstunden müssen task-spezifisch ausgewiesen werden:
für `GER` getrennt nach `25%` und `50%`, für `IND` getrennt nach `MO-Sa` und `So`.

## Akzeptanzkriterien

- Überstunden-Tasks werden aus CSV gelesen und netto aggregiert (inkl. Gegenbuchungen).
- Summary-Tabelle zeigt zwei getrennte Überstunden-Spalten.
- Spaltenüberschrift ist standortabhängig:
  - `GER`: `25%`, `50%`
  - `IND`: `MO-Sa`, `So`
- Detailtabelle zeigt On-Call- und Überstundenzeilen.
- Beim Öffnen/Refresh ist keine IA vorausgewählt; Detailtabelle bleibt leer bis Auswahl.

## Technische Umsetzung

- Overtime-Lader mit Taskfilter für vier fachliche Tasks.
- Aggregation in getrennte Buckets (`GER_25`, `GER_50`, `IND_MO_SA`, `IND_SO`).
- Monatsdialog um dynamische Header + Spaltenbefüllung erweitert.
- Selection-Handling im Monatsdialog stabilisiert.

## Betroffene Dateien

- `src/services/compensation_service.py`
- `src/app/application.py`
- `src/ui/monthly_compensation_dialog.py`
- `tests/test_compensation_service.py`

## Tests / Validierung

- `pytest tests/test_compensation_service.py`

