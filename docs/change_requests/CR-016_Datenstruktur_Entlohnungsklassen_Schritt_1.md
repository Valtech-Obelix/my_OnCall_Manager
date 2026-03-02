# CR-016 – Datenstruktur für Entlohnungsklassen anlegen (Schritt 1)

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-03-01
- Umgesetzt am: 2026-03-01
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-010

## Beschreibung (fachlich)

Für den neuen Use Case zur Erfassung von Entlohnungsklassen soll im ersten
Schritt die persistente Datenstruktur in der Datenbank angelegt werden.

## Akzeptanzkriterien

- Es existiert eine Tabelle zur Speicherung von Entlohnungsklassen.
- Gespeichert werden können: `typ`, `beschreibung`, `auszahlungsbetrag`,
  `buchungstask_name`.
- `auszahlungsbetrag` ist nicht negativ.

## Technische Umsetzung

- Neue Tabelle `entlohnungsklasse` im DB-Schema ergänzt:
  - `id` (PK)
  - `typ` (`TEXT NOT NULL`)
  - `beschreibung` (`TEXT NOT NULL`)
  - `auszahlungsbetrag` (`REAL NOT NULL CHECK >= 0`)
  - `buchungstask_name` (`TEXT NOT NULL`)

## Betroffene Dateien

- `src/infrastructure/database.py`
- `tests/test_database_schema.py`
- `docs/use_cases/UC-010_Entlohnungsklassen_verwalten.md`

## Tests / Validierung

- `PYTHONPATH=. .venv/bin/pytest -q tests/test_database_schema.py`
