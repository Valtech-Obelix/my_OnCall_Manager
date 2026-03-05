# CR-031 – Bestaetigungsdialog Loeschen mit deutschen Buttontexten

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-03-05
- Umgesetzt am: 2026-03-05
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-018

## Beschreibung (fachlich)

Im Dialog `Mitarbeiterverwaltung` waren die Buttons im
Loesch-Bestaetigungsdialog sprachlich inkonsistent (deutscher Meldungstext,
englische Buttons).

## Akzeptanzkriterien

- Der Loesch-Bestaetigungsdialog zeigt deutschen Meldungstext.
- Die Buttons sind deutsch beschriftet: `Ja` und `Nein`.

## Technische Umsetzung

- Statt der systemabhaengigen Standard-`QMessageBox.question(...)`-Buttons
  wird eine explizite `QMessageBox` mit `Ja`-/`Nein`-Buttons verwendet.

## Betroffene Dateien

- `src/ui/incident_analyst_dialog.py`
- `docs/change_requests/00_CR_Index.md`

## Tests / Validierung

- `.venv/bin/python -m py_compile src/ui/incident_analyst_dialog.py`
