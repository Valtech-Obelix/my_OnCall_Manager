# UC-017 – Gehaltsgruppen verwalten

## Version
0.1

---

## Ziel

Als Administrator  
moechte ich Gehaltsgruppen mit zeitabhaengigen Betraegen verwalten koennen,  
um den gueltigen Betrag je Gehaltsgruppe zu einem beliebigen Zeitpunkt abfragen zu koennen.

---

## Domänenobjekte

### Gehaltsgruppe

- Bezeichnung

### Gehaltsgruppen-Betrag

- Gehaltsgruppe
- Betrag
- Gueltig-ab-Datum

---

## Hauptablauf

1. Administrator legt eine Gehaltsgruppe mit Bezeichnung, Betrag und Gueltig-ab-Datum an.
2. System speichert die Gehaltsgruppe und den ersten Betragseintrag.
3. Administrator aendert spaeter den Betrag derselben Gehaltsgruppe.
4. System verlangt zwingend ein Gueltig-ab-Datum fuer die Aenderung.
5. System speichert den neuen Betrag als neue historische Version.
6. Ein aufrufender Prozess fragt den Betrag einer Gehaltsgruppe fuer einen Stichtag ab.
7. System liefert den zum Stichtag gueltigen Betrag.

---

## Akzeptanzkriterien

- Eine Gehaltsgruppe besteht mindestens aus `Bezeichnung` und historisierten `Betrag`-Eintraegen.
- Bei jeder Betragsaenderung ist das Feld `Gueltig-ab-Datum` verpflichtend.
- Es darf kein impliziter oder vorbefuellter Standard fuer `Gueltig-ab-Datum` verwendet werden.
- Pro Gehaltsgruppe darf ein `Gueltig-ab-Datum` nur einmal existieren.
- Die Stichtagsabfrage liefert den juengsten Betrag mit `gueltig_ab <= Stichtag`.
- Wenn vor dem Stichtag noch kein Betrag gueltig ist, wird kein Betrag geliefert.

---

## Zugehoerige Change Requests

- [CR-027 – Gehaltsgruppen mit Betragshistorie und Stichtagsabfrage](../change_requests/CR-027_Gehaltsgruppen_mit_Betragshistorie_und_Stichtagsabfrage.md)
