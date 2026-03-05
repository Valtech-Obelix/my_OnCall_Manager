# CR-027 – Gehaltsgruppen mit Betragshistorie und Stichtagsabfrage

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-03-05
- Umgesetzt am: 2026-03-05
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-017

## Beschreibung (fachlich)

Gehaltsgruppen sollen verwaltbar sein. Jede Gehaltsgruppe hat eine Bezeichnung.
Der Betrag ist historisiert zu fuehren, damit spaetere Aenderungen keinen
bestehenden Zeitraum ueberschreiben. Bei einer Betragsaenderung ist ein
Gueltig-ab-Datum zwingend anzugeben.

## Akzeptanzkriterien

- Es existiert eine persistente Struktur fuer Gehaltsgruppen.
- Es existiert eine persistente Struktur fuer historisierte Betragseintraege.
- Betragseintraege sind nicht negativ.
- Betragsaenderungen ohne `gueltig_ab` werden fachlich abgelehnt.
- Der gueltige Betrag kann fuer einen Stichtag abgefragt werden.
- Doppelbelegung eines `gueltig_ab` innerhalb derselben Gehaltsgruppe ist nicht erlaubt.

## Technische Umsetzung

- Neue Tabellen `gehaltsgruppe` und `gehaltsgruppe_betrag` im DB-Schema.
- FK-Beziehung und Unique-Constraint auf `(gehaltsgruppe_id, gueltig_ab)`.
- Repository + Service fuer Anlage, Betragsaenderung und Stichtagsabfrage.
- Validierungen fuer Pflichtfeld `gueltig_ab` und nicht-negative Betraege.

## Betroffene Dateien

- `src/infrastructure/database.py`
- `src/domain/gehaltsgruppe.py`
- `src/infrastructure/gehaltsgruppe_repository.py`
- `src/services/gehaltsgruppe_service.py`
- `src/app/application.py`
- `tests/test_database_schema.py`
- `tests/test_gehaltsgruppe_repository.py`
- `tests/test_gehaltsgruppe_service.py`
- `docs/use_cases/UC-017_Gehaltsgruppen_verwalten.md`

## Tests / Validierung

- `PYTHONPATH=. .venv/bin/pytest -q tests/test_database_schema.py tests/test_gehaltsgruppe_repository.py tests/test_gehaltsgruppe_service.py`
