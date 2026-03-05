# CR-022 – Task-Validierung im Vergleichsdialog inkl. Fehlergründe

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-03-05
- Umgesetzt am: 2026-03-05
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-016, UC-012

## Beschreibung (fachlich)

Der Dialog „Schichtplan vs. Buchungen vergleichen“ soll nicht nur IA/Schicht-Soll-Ist
prüfen, sondern auch den gebuchten Task gegen die Standortregel validieren.
Fehlerhafte Buchungen müssen mit unterscheidbaren Fehlergründen angezeigt werden.

## Akzeptanzkriterien

- Task-Prüfung für `GER` und `IND` gemäß UC-016-Regeln.
- Eine Buchung kann trotz korrektem IA/Slot als fehlerhaft markiert werden, wenn der Task falsch ist.
- Tooltip enthält konkrete Gründe (z. B. falscher Task, Buchung nicht erlaubt).
- Bestehende Soll/Ist-Abweichungen bleiben erhalten.

## Technische Umsetzung

- Fachregel „erwarteter Task je Standort/Tagtyp/Slot“ zentral im `CompensationService`.
- Vergleichsdialog liest Tasknamen aus CSV und prüft gegen erwarteten Task.
- Tooltip-Logik um differenzierte Fehlerursachen erweitert.

## Betroffene Dateien

- `src/services/compensation_service.py`
- `src/ui/shift_booking_compare_dialog.py`
- `docs/use_cases/UC-016_Schichtplan_vs_Buchungen_auf_Task_erweitern.md`

## Tests / Validierung

- `pytest tests/test_compensation_service.py`

