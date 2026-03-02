# CR-019 – Umbau IA-Erfassungsoberfläche analog Standortdialog

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-03-01
- Umgesetzt am: 2026-03-01
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-001, UC-002, UC-003, UC-007, UC-011

## Beschreibung (fachlich)

Die Oberfläche zur Verwaltung der Incident-Analysten soll analog zum
Rufbereitschaftsstandort-Dialog aufgebaut werden: kombinierte Anzeige und
Erfassung/Bearbeitung in einem gemeinsamen Dialog.

## Akzeptanzkriterien

- Dialog mit 2 Hauptbereichen: links Anzeige, rechts Edit.
- Unterer linker Bereich enthält fachliche Aktionen (`Neu`, `Bearbeiten`,
  `Speichern`, `Deaktivieren`, `Löschen`).
- Unterer rechter Bereich enthält Dialogsteuerung (`Schließen`).
- Auswahl in der Tabelle lädt die Daten in den Edit-Bereich.
- Eingabefelder sind standardmäßig deaktiviert und werden erst durch `Neu` oder
  `Bearbeiten` aktiv.
- `Speichern` legt neu an oder aktualisiert den ausgewählten Datensatz.

## Technische Umsetzung

- `IncidentAnalystDialog` vollständig auf kombiniertes Grid-Layout umgebaut.
- Bisherige separaten Subdialoge für Add/Edit werden im Hauptablauf nicht mehr genutzt.
- Tabellenansicht ergänzt um relevante IA-Daten inkl. Standort.
- Filter (`Alle`, `Aktiv`, `Inaktiv`) im Anzeige-Bereich integriert.
- Edit-Bereich enthält alle IA-Felder:
  Vorname, Nachname, E-Mail, OpsGenie ID, Standort, Startdatum, optional Enddatum.

## Betroffene Dateien

- `src/ui/incident_analyst_dialog.py`

## Tests / Validierung

- `python3 -m compileall src tests`

