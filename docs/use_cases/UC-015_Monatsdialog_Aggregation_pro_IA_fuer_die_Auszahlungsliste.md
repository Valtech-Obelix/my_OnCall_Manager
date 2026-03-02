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
3. Admin wählt Jahr und Monat aus.
4. System aggregiert alle Schichten des gewählten Monats pro IA.
5. System zeigt pro IA Standort, Schichtanzahl (`F`, `T`, `S`) und Auszahlung in EUR.
6. System zeigt die Gesamtsumme über alle IAs.
7. Admin schließt den Dialog über die Buttonleiste mit `Schließen`.

---

## Akzeptanzkriterien

- Eigener Dialog ist über das Hauptfenster erreichbar.
- Monat/Jahr können gewählt werden.
- Pro IA werden mindestens folgende Felder angezeigt:
  - Buchungsname
  - Standort
  - Anzahl `Früh`, `Tag`, `Spät`
  - Auszahlung in EUR
- Die Gesamtsumme des Monats wird angezeigt.
- Die Berechnung nutzt die in UC-014 definierten Entlohnungsregeln.
