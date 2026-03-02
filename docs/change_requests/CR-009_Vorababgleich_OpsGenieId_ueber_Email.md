# CR-009 – Vorababgleich fehlender `opsgenie_id` über E-Mail

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-02-28
- Umgesetzt am: 2026-02-28
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-004

## Beschreibung (fachlich)

Vor dem eigentlichen Schichtimport soll das System prüfen, ob in den gelieferten
Schichten `opsgenie_id`-Werte vorkommen, die in `incident_analyst.opsgenie_id`
noch nicht gepflegt sind.  
Wenn für solche Einträge eine Zuordnung über die E-Mail im Feld `recipient.name`
möglich ist, soll `opsgenie_id` im passenden Incident-Analyst-Datensatz automatisch
ergänzt werden.

## Akzeptanzkriterien

- Der Vorababgleich läuft vor dem Speichern der Schichten.
- Für unbekannte `opsgenie_id` wird ein Fallback-Matching über E-Mail versucht.
- Bei erfolgreichem E-Mail-Match wird `incident_analyst.opsgenie_id` ergänzt.
- Konflikte (abweichende bereits gesetzte `opsgenie_id`) werden nicht überschrieben,
  sondern geloggt.

## Technische Umsetzung

- Vorverarbeitung der Timeline im `OpsGenieService` ergänzt.
- Neue Repository-Methode `update_opsgenie_id(...)` ergänzt.
- Importlogik bleibt primär auf Lookup über `opsgenie_id`.
- Service-/Repository-Tests für Auto-Mapping und Konfliktfall ergänzt.

## Betroffene Dateien

- `src/services/opsgenie_service.py`
- `src/infrastructure/incident_analyst_repository.py`
- `tests/test_opsgenie_service.py`
- `tests/test_incident_analyst_repository.py`
- `docs/use_cases/UC-004_Aktuellen_Schichtplan_aus_Opsgenie_lesen`

## Tests / Validierung

- `python3 -m compileall src tests`
- `.venv/bin/python -m pytest -q`
