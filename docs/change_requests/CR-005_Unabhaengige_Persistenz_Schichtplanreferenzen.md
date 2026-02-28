# CR-005 – Schichtplan-Referenzen unabhängig persistieren

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-02-27
- Umgesetzt am: 2026-02-27
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-005

## Beschreibung (fachlich)

Die Informationen über `Schedule ID` und `Name des Schichtplans` müssen unabhängig von den Tabellen `shifts` und `import_history` gespeichert werden, damit sie beim Leeren dieser Tabellen erhalten bleiben.

## Akzeptanzkriterien

- Es existiert eine eigene Persistenz für Schichtplan-Referenzen.
- Nach dem Leeren von `shifts` und `import_history` bleiben die Schichtplan-Referenzen erhalten.
- Der Import-Dialog lädt die Auswahl aus dieser unabhängigen Persistenz.

## Technische Umsetzung

- Neue Tabelle `schedule_registry` eingeführt (`schedule_id`, `schedule_name`, `last_used`).
- Beim Import wird die Referenz per Upsert in `schedule_registry` gespeichert.
- UI-Auswahl (`Name des Schichtplans`) basiert auf `schedule_registry` statt auf `import_history`.
- Bestehende Import-Historie bleibt für Importlogik erhalten.

## Betroffene Dateien

- `src/infrastructure/database.py`
- `src/infrastructure/shift_repository.py`
- `src/services/opsgenie_service.py`
- `src/ui/opsgenie_import_dialog.py`
- `tests/test_shift_repository.py`
- `tests/test_opsgenie_service.py`

## Tests / Validierung

- `python3 -m compileall src tests`
- `.venv/bin/python -m pytest -q`
