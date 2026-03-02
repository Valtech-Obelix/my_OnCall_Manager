# CR-013 – Button „Anzeige aktualisieren“ mit Dirty-State

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-02-28
- Umgesetzt am: 2026-02-28
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-008

## Beschreibung (fachlich)

Der bisherige Button `Anzeigen` soll in `Anzeige aktualisieren` umbenannt
werden.  
Er soll nur dann aktiv sein, wenn seit der letzten Darstellung mindestens ein
Parameter geändert wurde (Schichtplan, Ansicht, Zeitraum, Checkbox).  
Nach einer Aktualisierung wird der Button wieder deaktiviert.

## Akzeptanzkriterien

- Button-Label lautet `Anzeige aktualisieren`.
- Button ist initial deaktiviert.
- Nach Änderung eines Parameters wird der Button aktiv.
- Nach Klick auf den Button und erfolgreicher Aktualisierung wird er wieder
  deaktiviert.

## Technische Umsetzung

- Neuer Dirty-State im Dialog eingeführt.
- Parameteränderungen markieren den Zustand als „aktualisieren ausstehend“.
- Klick auf den Button rendert neu und setzt den Dirty-State zurück.

## Betroffene Dateien

- `src/ui/shift_plan_view_dialog.py`

## Tests / Validierung

- `python3 -m compileall src/ui/shift_plan_view_dialog.py`
