# CR-033 – Gehaltsklassenzuordnung zu Mitarbeitern mit Zeitraum

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-03-05
- Umgesetzt am: 2026-03-05
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-019

## Beschreibung (fachlich)

Mitarbeiter sollen Gehaltsklassen mit Gueltigkeitszeitraum zugeordnet bekommen.
Dabei sind erstmalige Zuordnungen, Wechsel (neuer Zeitraum) und Korrekturen
(gleicher Zeitraum, anderer Wert) zu unterstuetzen.

## Akzeptanzkriterien

- Zuordnung kann in der Mitarbeiter-Bearbeitungsmaske gepflegt werden.
- Ueberlappende Zeitraeume je Mitarbeiter sind nicht erlaubt.
- Wechsel wird als neue Zuordnung gespeichert.
- Korrektur mit gleichem Zeitraum ueberschreibt nur die Gehaltsklasse.
- Stichtagsabfrage liefert die gueltige Zuordnung.
- Gehaltsgruppenliste im Zuordnungsdialog ist auf den Standort des Mitarbeiters eingeschraenkt.

## Technische Umsetzung

- Neue Tabelle `mitarbeiter_gehaltsgruppe` inkl. FK und Zeitraumfeldern.
- Repository um Methoden fuer Verlauf, Upsert und Stichtag erweitert.
- Neuer Service `MitarbeiterGehaltsgruppeService` mit Ueberlappungspruefung.
- Mitarbeiterdialog um Gehaltsklasse + Gueltig-ab/Gueltig-bis erweitert.
- Application-Fassade um Zuordnungsfunktionen ergaenzt.
- Dialoglogik fuer Gehaltsgruppe-Auswahl filtert Gruppen anhand des Mitarbeiters.

## Betroffene Dateien

- `src/infrastructure/database.py`
- `src/infrastructure/incident_analyst_repository.py`
- `src/services/mitarbeiter_gehaltsgruppe_service.py`
- `src/app/application.py`
- `src/ui/incident_analyst_dialog.py`
- `tests/test_database_schema.py`
- `tests/test_mitarbeiter_gehaltsgruppe_service.py`
- `docs/use_cases/UC-019_Zuordnung_von_Gehaltsklassen_zu_Mitarbeitern`
- `docs/change_requests/00_CR_Index.md`

## Tests / Validierung

- `PYTHONPATH=. .venv/bin/pytest -q tests/test_database_schema.py tests/test_mitarbeiter_gehaltsgruppe_service.py`
