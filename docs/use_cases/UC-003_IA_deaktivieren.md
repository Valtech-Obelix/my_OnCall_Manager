# UC-003 – IA deaktivieren

## Ziel
Als           Administrator  
möchte        ich einen bestehenden Incident-Analysten aus der Liste auswählen und diesen durch Eingabe eines Enddatums deaktivieren können  
um            die verfügbaren Incident-Analysten verwalten zu können.

---

## Modul-Zuordnung
- UI.           : incident_analyst_dialog.py  
- Geschäftslogik: incident_analyst_service.py  
- Datenhaltung. : incident_analyst_repository.py  
- Domain.       : incident_analyst.py  

---

## Akteur
Administrator

---

## Vorbedingungen
- Mindestens ein Incident-Analyst existiert.
- Der Incident-Analyst ist aktuell aktiv (kein Enddatum gesetzt).

---

## Trigger
- Auswahl „Incident Analysten verwalten“
- Auswahl eines Incident-Analysten
- Klick auf „Deaktivieren“-Button

---

## Hauptablauf
01. Administrator öffnet den Verwaltungsdialog.
02. System zeigt die Liste der aktuellen Incident-Analysten an.
03. Administrator wählt einen aktiven Incident-Analysten aus.
04. Administrator klickt auf „Deaktivieren“.
05. System öffnet einen Dialog zur Eingabe des Enddatums.
06. Administrator wählt ein Enddatum.
07. System validiert:
     - Enddatum ≥ Startdatum
08. System speichert das Enddatum in der Datenbank.
09. System aktualisiert die Liste.
10. Der Analyst wird als „deaktiviert“ gekennzeichnet dargestellt.

---

## Alternativabläufe

### A1 – Kein Analyst ausgewählt
- Deaktivieren-Button ist deaktiviert.
- Keine Aktion möglich.

### A2 – Analyst ist bereits deaktiviert
- Deaktivieren-Button ist deaktiviert oder Fehlermeldung wird angezeigt.

### A3 – Enddatum < Startdatum
- Fehlermeldung wird angezeigt.
- Speicherung wird abgebrochen.

### A4 – Benutzer bricht ab
- Keine Änderung erfolgt.

### A5 – Datenbankfehler
- Fehler wird geloggt.
- Fehlermeldung wird angezeigt.

---

## Akzeptanzkriterien
- Ein aktiver Analyst kann deaktiviert werden.
- Das Enddatum wird korrekt gespeichert.
- Enddatum darf nicht vor Startdatum liegen.
- Ein bereits deaktivierter Analyst kann nicht erneut deaktiviert werden.
- Deaktivierte Analysten sind optisch erkennbar.

---

## Technische Hinweise

### Domain
- Attribut `ende_datum` wird gesetzt.
- Validierung bereits vorhanden:
  - ende_datum >= start_datum

### Service
- Neue Methode:
  deactivate(p_id: int, p_ende_datum: date)

### Repository
- Neue Methode:
  update_end_date(p_id: int, p_ende_datum: date)

### UI
- Neuer Button „Deaktivieren“
- Neuer Dialog mit QDateEdit
- Optische Kennzeichnung deaktivierter Einträge (z. B. "(deaktiviert)" oder graue Schrift)

---

## Abgrenzung
- Löschen erfolgt ausschließlich über UC-002.
- Anlegen erfolgt ausschließlich über UC-001.

---

## Status
geplant

## Version
0.1