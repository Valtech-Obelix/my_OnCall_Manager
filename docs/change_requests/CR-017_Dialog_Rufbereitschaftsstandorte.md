# CR-017 – Kombinierter Anzeige-/Erfassungsdialog für Rufbereitschaftsstandorte

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-03-01
- Umgesetzt am: 2026-03-01
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-011

## Beschreibung (fachlich)

Rufbereitschaftsstandorte sollen in einem kombinierten Anzeige- und
Erfassungsdialog verwaltet werden können.  
Der Dialog enthält links die Anzeige, rechts den Edit-Bereich, unten links
`Button 1` für inhaltliche Aktionen und unten rechts `Button 2` für die
Dialogsteuerung.

## Akzeptanzkriterien

- Dialog über Hauptfenster erreichbar.
- Tabelle mit zwei Spalten `ID` und `Name`.
- `ID` genau 3 Zeichen, `Name` maximal 30 Zeichen.
- Dialogaufteilung gemäß beschriebenem 4-Bereichsaufbau.

## Technische Umsetzung

- Neue Tabelle `rufbereitschaftsstandort` im Schema.
- Neues Repository `OnCallLocationRepository` für CRUD.
- Neue Application-Methoden für Zugriff aus UI.
- Neuer Dialog `OnCallLocationDialog`.
- Neuer Button im Hauptmenü.

## Betroffene Dateien

- `src/infrastructure/database.py`
- `src/infrastructure/oncall_location_repository.py`
- `src/app/application.py`
- `src/ui/oncall_location_dialog.py`
- `src/ui/main_window.py`
- `tests/test_oncall_location_repository.py`
- `tests/test_database_schema.py`
- `docs/use_cases/UC-011_Rufbereitschaftsstandorte_anzeigen_und_erfassen.md`

## Tests / Validierung

- `PYTHONPATH=. .venv/bin/pytest -q tests/test_oncall_location_repository.py tests/test_database_schema.py`
