# UC-015 – Monatsdialog: Aggregation pro IA für die Auszahlungsliste

## Version
0.1

---

## Ziel

Als Admin  
möchte ich für einen Monat eine aggregierte Auszahlungsliste pro Incident Analyst sehen,  
um die Auszahlungssumme je IA und gesamt nachvollziehen zu können.

---

## Hauptablauf

1. Admin öffnet den Dialog „Monatsabrechnung IA-Auszahlung“.
2. System setzt standardmäßig den Vormonat.
3. System setzt den Standortfilter standardmäßig auf `Deutschland (GER)`.
4. Admin wählt Jahr, Monat und Standort aus.
5. System aggregiert alle Buchungen (`On Call`) des gewählten Monats für den gewählten Standort pro IA.
6. System zeigt pro IA Standort, Schichtanzahl (`F`, `T`, `S`) und Auszahlung in EUR.
7. Admin wählt eine IA-Zeile in der Übersicht aus.
8. System zeigt in einer Detailtabelle die Buchungen, die zur Auszahlung geführt haben.
9. System zeigt die Gesamtsumme über alle IAs.
10. Admin schließt den Dialog über die Buttonleiste mit `Schließen`.

---

## Akzeptanzkriterien

- Eigener Dialog ist über das Hauptfenster erreichbar.
- Monat/Jahr können gewählt werden.
- Standort kann über ein Auswahlfeld gewählt werden.
- Vorauswahl beim Öffnen ist `Deutschland (GER)`.
- Pro IA werden mindestens folgende Felder angezeigt:
  - Buchungsname
  - Standort
  - Anzahl `Früh`, `Tag`, `Spät`
  - Auszahlung in EUR
- Bei Auswahl einer IA-Zeile werden Detailbuchungen in einer zweiten Tabelle angezeigt.
- Die Gesamtsumme des Monats wird angezeigt.
- Die Berechnung nutzt die in UC-014 definierten Entlohnungsregeln.
- Grundlage der Berechnung sind Buchungen (CSV), nicht der OpsGenie-Schichtplan.
