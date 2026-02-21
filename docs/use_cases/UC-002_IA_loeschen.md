# UC-002 – IA Löschen

## Ziel
Als           Administrator  
möchte        ich einen bestehenden Incident-Analysten aus der Liste auswählen und löschen können  
um            die verfügbaren Incident-Analysten verwalten zu können.

---

## Modul-Zuordnung
- UI.           : incident_analyst_dialog.py  
- Geschäftslogik: application.py  
- Datenhaltung. : incident_analyst_repository.py  
- Domain.       : keine Änderung  

---

## Akteur
Administrator

---

## Vorbedingungen
- Mindestens ein Incident-Analyst ist vorhanden.

---

## Trigger
- Auswahl „Incident Analysten verwalten“
- Klick auf 🗑 Button im IncidentAnalystDialog

---

## Hauptablauf
01. Administrator öffnet den Verwaltungsdialog.
02. System zeigt Liste der aktuellen Incident-Analysten an.
03. Administrator wählt einen Incident-Analysten explizit aus.
04. Delete-Button wird aktiv.
05. Administrator klickt auf 🗑.
06. System zeigt Sicherheitsabfrage.
07. Administrator bestätigt.
08. System löscht den Incident-Analysten aus der Datenbank.
09. System aktualisiert die Liste.

---

## Alternativabläufe

### A1 – Kein Analyst ausgewählt
- Delete-Button ist deaktiviert.
- Keine Aktion möglich.

### A2 – Benutzer bricht Sicherheitsabfrage ab
- Löschvorgang wird abgebrochen.
- Keine Datenänderung erfolgt.

### A3 – Datenbankfehler
- Löschvorgang schlägt fehl.
- Fehlermeldung wird angezeigt.
- Log-Eintrag wird erzeugt (optional zukünftige Erweiterung).

---

## Akzeptanzkriterien
- Ein Analyst wird nur gelöscht, wenn er explizit ausgewählt wurde.
- Es erfolgt eine Sicherheitsabfrage.
- Nach dem Löschen wird die Liste aktualisiert.
- Der Eintrag ist aus der Datenbank entfernt.

---

## Technische Hinweise

### UI
- QListWidget mit Speicherung der ID über Qt.UserRole.
- Delete-Button initial deaktiviert.
- Aktivierung nur bei expliziter Auswahl.

### Repository
- Methode: delete(p_id: int)

### Application
- Methode: delete_incident_analyst(p_id: int)

### Sicherheitsmechanismus
- Keine Vorauswahl beim Laden der Liste.
- Button-Zustand wird über itemSelectionChanged gesteuert.

---

## Abgrenzung
- Deaktivierung eines Incident-Analysten erfolgt nicht über diesen Use Case.
- Deaktivierung wird in UC-003 behandelt (Enddatum setzen).

---

## Status
implementiert

## Version
0.1