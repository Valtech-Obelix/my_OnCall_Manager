# UC-001 – IA Anlegen

## Ziel
Als           Administrator
möchte        ich einen neuen Incident-Analysten mit Vorname, Nachname, Email-Adresse sowie Gültigkeitszeitraum anlegen können
um            die verfügbaren Incident-Analysten verwalten zu können.

## Modul-Zuordnung
- UI.           : main_window.py
- Geschäftslogik: incident_analyst.py
- Datenhaltung. : incident_analyst_repository.py, 
                  database.py

## Akteur
Administrator

## Vorbedingungen
- keine

## Trigger
- Auswahl "Incident Analyst anlegen" im Hauptfenster

## Hauptablauf
01. Admin startet das Programm
02. Admin öffnet "Neuer Incident Analyst"
03. Admin erfasst Vorname
04. Admin erfasst Nachname
05. Admin erfasst Email-Adresse
06. Admin erfasst Startdatum
07. Admin erfasst Enddatum (optional)
08. Admin klickt auf "Speichern"
09. System validiert die Eingaben
10. System erzeugt automatisch den Buchungsnamen
11. System speichert die Daten in der SQLite-Datenbank

## Alternativabläufe

### A1 – Validierungsfehler
- Pflichtfelder fehlen
- Email-Format ungültig
- Enddatum < Startdatum
→ Fehlermeldung wird angezeigt
→ Speicherung wird abgebrochen

### A2 – Datenbankfehler
- SQLite-Verbindung nicht verfügbar
- Constraint-Verletzung
→ Fehlermeldung anzeigen
→ Log-Eintrag erzeugen

## Akzeptanzkriterien
- Der Incident-Analyst ist mit allen erfassten Daten korrekt gespeichert.
- Der Buchungsname wird automatisch generiert.
- Datumslogik ist korrekt geprüft.
- Bei Fehlern erfolgt keine Speicherung.

## Technische Hinweise

### Betroffene Klassen
- main.py
- application.py
- incident_analyst.py
- incident_analyst_repository.py
- database.py
- main_window.py

### Neue/angepasste Attribute (Entity)
- vorname: str
- nachname: str
- email: str
- buchungsname: str (abgeleitet)
- start_datum: date
- end_datum: date | None

### Buchungsname-Regel
Format:
<Nachname>, <Vorname>

Beispiel:
Muster, Max

### DB-Änderungen
Tabelle: incident_analyst

Neue Spalten:
- vorname                              TEXT NOT NULL
- nachname                             TEXT NOT NULL
- buchungsname                         TEXT NOT NULL
- start_datum                          DATE NOT NULL
- end_datum                            DATE NULL

### Validierungen
- vorname != ''
- nachname != ''
- gültiges Email-Format
- start_datum Pflichtfeld
- end_datum >= start_datum (falls gesetzt)

## Status
geplant

## Änderungsverlauf

### Version 0.2
- Erweiterung um Vorname und Nachname
- Einführung Gültigkeitszeitraum (Start-/Enddatum)
- Buchungsname wird automatisch generiert
- Anpassung Datenbankschema

### Version 0.1
- IA mit Name und Email
