# UC-009 – Aktive IA nach Schichtanzahl anzeigen

## Version
0.1

---

## Ziel

Als Administrator  
möchte ich eine Tabelle sehen, die alle aktiven Incident Analysts nach der Anzahl
ihrer Schichten in den letzten `n` Wochen absteigend sortiert darstellt,
um die aktuelle On-Call-Belastung schnell vergleichen zu können.

---

## Hauptablauf

1. Administrator öffnet den Dialog „Aktive IA Schichtanzahl anzeigen“.
2. System schlägt den zuletzt verwendeten Wert für `n` vor.
3. Administrator gibt `n` (Wochen) ein und klickt auf „Anzeigen“.
4. System zeigt eine Tabelle mit:
   - Buchungsname
   - Anzahl der Schichten in den letzten `n` Wochen
5. System sortiert die Tabelle absteigend nach Schichtanzahl.
6. System speichert den verwendeten Wert für `n` als neuen Vorschlagswert.

---

## Akzeptanzkriterien

- Nur aktive Incident Analysts werden aufgelistet.
- Spalten sind `Buchungsname` und `Schichtanzahl`.
- Sortierung erfolgt absteigend nach `Schichtanzahl`.
- `n` ist durch den Administrator eingabefähig.
- Beim erneuten Öffnen ist der zuletzt verwendete `n`-Wert vorbelegt.

## Zugehörige Change Requests

- [CR-015 – Dialog „Aktive IA Schichtanzahl“ inkl. persistiertem Wochenwert](../change_requests/CR-015_Dialog_Aktive_IA_Schichtanzahl.md)
