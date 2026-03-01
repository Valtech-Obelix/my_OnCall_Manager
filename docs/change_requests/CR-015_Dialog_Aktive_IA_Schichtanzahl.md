# CR-015 – Dialog „Aktive IA Schichtanzahl“ inkl. persistiertem Wochenwert

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-03-01
- Umgesetzt am: 2026-03-01
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-009

## Beschreibung (fachlich)

Das System soll einen Dialog bereitstellen, der alle aktiven Incident Analysts
nach der Anzahl ihrer Schichten in den letzten `n` Wochen sortiert anzeigt.  
`n` wird durch den Administrator eingegeben; der zuletzt verwendete Wert wird
beim nächsten Öffnen automatisch vorgeschlagen.

## Akzeptanzkriterien

- Tabelle enthält `Buchungsname` und `Schichtanzahl`.
- Es werden ausschließlich aktive IA berücksichtigt.
- Sortierung ist absteigend nach `Schichtanzahl`.
- Eingabefeld für `n` ist vorhanden.
- Der zuletzt verwendete `n`-Wert wird gespeichert und wiederverwendet.

## Technische Umsetzung

- Neuer UI-Dialog `IncidentAnalystShiftCountDialog`.
- Neuer Menüeintrag im Hauptfenster.
- Neue Repository-Abfrage für Schichtanzahl aktiver IA im Zeitraum.
- Neue Tabelle `app_settings` für persistente einfache UI-Parameter.

## Betroffene Dateien

- `src/ui/incident_analyst_shift_count_dialog.py`
- `src/ui/main_window.py`
- `src/app/application.py`
- `src/infrastructure/shift_repository.py`
- `src/infrastructure/database.py`
- `tests/test_shift_repository.py`
- `docs/use_cases/UC-009_Aktive_IA_nach_Schichtanzahl.md`

## Tests / Validierung

- `PYTHONPATH=. .venv/bin/pytest -q tests/test_shift_repository.py`
- `python3 -m compileall src`
