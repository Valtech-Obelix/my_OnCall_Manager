# UC-011 – Rufbereitschaftsstandorte anzeigen und erfassen

## Version
0.1

---

## Ziel

Als Administrator  
möchte ich Rufbereitschaftsstandorte anzeigen und erfassen können,  
um die späteren Prozesse zur Schicht- und Zahlungsfreigabe vorzubereiten.

---

## Hauptablauf

1. Administrator öffnet den Dialog „Rufbereitschaftsstandorte“ über das Hauptfenster.
2. System zeigt links die Standorttabelle mit den Spalten `ID` und `Name`.
3. Administrator erfasst oder bearbeitet rechts die Felder `ID` und `Name`.
4. Administrator steuert den Inhalt über `Button 1` (z. B. Neu, Speichern, Löschen, Aktualisieren).
5. Administrator steuert den Dialog über `Button 2` (Schließen).

---

## Akzeptanzkriterien

- Der Dialog ist über einen eigenen Button im Hauptfenster erreichbar.
- Die Tabelle zeigt genau zwei Spalten: `ID`, `Name`.
- `ID` ist ein Textfeld mit genau 3 Zeichen.
- `Name` ist ein Textfeld mit maximal 30 Zeichen.
- Der Dialog enthält getrennte Button-Bereiche:
  - `Button 1`: Steuerung innerhalb des Dialoginhalts
  - `Button 2`: Steuerung des Dialogs selbst

## Zugehörige Change Requests

- [CR-017 – Kombinierter Anzeige-/Erfassungsdialog für Rufbereitschaftsstandorte](../change_requests/CR-017_Dialog_Rufbereitschaftsstandorte.md)
