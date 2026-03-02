# UC-007 – IA bearbeiten

## Ziel
Als Administrator  
möchte ich die Daten eines bereits erfassten Incident-Analysten bearbeiten können  
um fehlerhafte oder geänderte Stammdaten direkt korrigieren zu können.

## Modul-Zuordnung
- UI.           : `incident_analyst_dialog.py`, `incident_analyst_edit_dialog.py`
- Geschäftslogik: `incident_analyst_service.py`
- Datenhaltung. : `incident_analyst_repository.py`, `database.py`

## Akteur
Administrator

## Vorbedingungen
- Mindestens ein Incident-Analyst ist im System vorhanden.

## Trigger
- Auswahl eines Incident-Analysten im Verwaltungsdialog.
- Klick auf die Aktion „Bearbeiten“.

## Hauptablauf
1. Administrator öffnet den Verwaltungsdialog.
2. Administrator markiert einen Incident-Analysten.
3. Administrator klickt auf „Bearbeiten“.
4. System öffnet einen Edit-Dialog mit vorausgefüllten Feldern.
5. Administrator passt gewünschte Felder an (`Vorname`, `Nachname`, `E-Mail`, `OpsGenie ID`, `Startdatum`, optional `Enddatum`).
6. Administrator klickt auf „Speichern“.
7. System validiert die Eingaben.
8. System speichert die Änderungen.
9. System aktualisiert die Liste.

## Alternativabläufe

### A1 – Validierungsfehler
- Fehlerhafte Eingaben (z. B. ungültiges E-Mail-Format, Enddatum vor Startdatum)
- System zeigt Fehlermeldung
- Keine Speicherung

### A2 – Datensatz nicht gefunden
- Der Datensatz existiert beim Speichern nicht mehr
- System zeigt Fehlermeldung
- Keine Speicherung

## Akzeptanzkriterien
- Ein Bearbeiten-Button ist im Verwaltungsdialog vorhanden.
- Der Edit-Dialog ist mit den aktuellen Daten vorausgefüllt.
- Änderungen werden nach Speichern dauerhaft in der DB übernommen.
- `opsgenie_id` kann mitgepflegt werden.
- Nach erfolgreichem Speichern wird die Liste aktualisiert.

## Status
abgeschlossen

## Version
0.1
