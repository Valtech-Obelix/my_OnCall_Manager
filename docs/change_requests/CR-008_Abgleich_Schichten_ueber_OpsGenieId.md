# CR-008 – Abgleich Schichten mit Incident-Analysten über `opsgenie_id`

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-02-28
- Umgesetzt am: 2026-02-28
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-004

## Beschreibung (fachlich)

Der Abgleich von Schicht-Einträgen zu Incident-Analysten soll nicht mehr über die
E-Mail im Feld `recipient.name`, sondern über die stabile OpsGenie-User-ID
`recipient.id` gegen `incident_analyst.opsgenie_id` erfolgen.

## Akzeptanzkriterien

- Analyst-Zuordnung im Import erfolgt über `recipient.id` -> `opsgenie_id`.
- Das Feld `recipient.name` wird für den Abgleich nicht mehr verwendet.
- Fehlende oder nicht zuordenbare `opsgenie_id` werden als `skipped` geloggt.

## Technische Umsetzung

- `OpsGenieService` auf Lookup über `recipient.id` umgestellt.
- Neue Repository-Methode `find_by_opsgenie_id(...)` ergänzt.
- Skip-Logging-Gründe auf `opsgenie_id`-Kontext angepasst.
- Tests für Service und Repository angepasst/ergänzt.

## Betroffene Dateien

- `src/services/opsgenie_service.py`
- `src/infrastructure/incident_analyst_repository.py`
- `tests/test_opsgenie_service.py`
- `tests/test_incident_analyst_repository.py`
- `docs/use_cases/UC-004_Aktuellen_Schichtplan_aus_Opsgenie_lesen`

## Tests / Validierung

- `python3 -m compileall src tests`
- `.venv/bin/python -m pytest -q`
