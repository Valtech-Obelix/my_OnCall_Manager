# CR-032 – Neu-Aktion leert Form nach abgebrochenem Loeschen

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-03-05
- Umgesetzt am: 2026-03-05
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-018

## Beschreibung (fachlich)

Wenn im Dialog `Mitarbeiterverwaltung` ein Loeschvorgang abgebrochen wurde,
uebernahm die anschliessende Aktion `Neu` faelschlich die zuvor ausgewaehlten
Mitarbeiterdaten.

## Akzeptanzkriterien

- Nach `Neu` sind die Eingabefelder leer.
- Es wird kein zuvor ausgewaehlter Mitarbeiter in die Felder zurueckgeschrieben.

## Technische Umsetzung

- Beim Leeren der Form wird die Tabellenauswahl signal-sicher entfernt
  (`blockSignals`, `clearSelection`, `setCurrentCell(-1, -1)`).
- Dadurch greift der Selection-Handler nicht mehr mit veralteter Auswahl.

## Betroffene Dateien

- `src/ui/incident_analyst_dialog.py`
- `docs/change_requests/00_CR_Index.md`

## Tests / Validierung

- `.venv/bin/python -m py_compile src/ui/incident_analyst_dialog.py`
