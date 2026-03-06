# UC-021 – Verwaltung des Budgets

## Version
0.2

---

## Ziel

Als Admin
möchte ich Budgets inkl. Herkunft und Geltungszeitraum erfassen, bearbeiten und einsehen,
um die verfügbare Finanzmasse über das Jahr (sowie im Monatsverlauf) belastbar steuern zu können.

---

## Hintergrund

Ein Vertragsjahr kann über mehrere Budgetquellen finanziert werden.

Beispiel:
- Kunde A: 5.000 EUR für 01.01.2026 – 30.03.2026
- Kunde B: 12.000 EUR für 01.01.2026 – 30.06.2026
- Kunde C: 8.000 EUR für 16.03.2026 – 30.09.2026

Der Use Case soll diese Blöcke vollständig abbilden, editieren können und den Gesamtverlauf darstellen.

---

## Vorbedingungen

- Incident-Analysten- und Kostenauswertung sind eingerichtet.
- Monatskosten können berechnet werden (bestehende Buchungs-Logik aus UC-020 ist vorhanden).
- Eine SQLite-Datenbank ist initialisiert.
- Der Admin hat Schreibzugriff auf die App-Daten.

---

## Begriffe

- Budgetquelle: ein externer Finanzierungspartner (z. B. Kunde/Projekt/Kostenstelle).
- Budgetperiode: ein Zeitfenster mit einem Betrag, zugeordnet zu genau einer Budgetquelle.

---

## Sollzustand (fachlich)

1. Admin kann neue Budgetquellen anlegen, ändern und deaktivieren.
2. Admin kann zu jeder Budgetquelle beliebig viele Budgetperioden anlegen.
3. Jede Budgetperiode besitzt:
   - Betrag in EUR
   - Beginn (`gueltig_ab`)
   - Ende (`gueltig_bis`, verpflichtend)
   - optionale Beschreibung
4. Das System zeigt eine Gesamtbudget-Ansicht über die Zeit, mindestens monatlich aggregiert.
5. Für jede betrachtete Zeitperiode werden alle aktiven Budgetperioden addiert.
6. Die Daten sind editierbar, inkl. Korrektur von Datum/Betrag.

---

## Fachliche Regeln und Annahmen (für Umsetzung)

### Zeitsystem
- Standardzeiteinheit für die Gesamtdarstellung: Monat.
- `gueltig_ab` und `gueltig_bis` sind inklusiv.
- `gueltig_bis` ist verpflichtend und muss vollständig gepflegt sein.

### Mehrfachperioden/Überlappung
- Mehrere Budgetquellen dürfen überlappen.
- Perioden derselben Quelle dürfen prinzipiell mehrfach überlappen; das kann bewusst zur Korrektur genutzt werden.
- Es erfolgt kein automatisches Verrechnen/Negieren durch Überlappung; jede Periode wird additiv berücksichtigt.

### Validierung
- `gueltig_ab` ist Pflicht.
- `gueltig_bis` ist Pflicht und muss >= `gueltig_ab` sein.
- Betrag muss >= 0 sein.
- Budgetquelle benötigt mindestens einen Namen.

### Darstellungslogik Gesamtbudget
- Gesamtbudget pro Monat = Summe der anteiligen Monatsbeträge der aktiven Budgetperioden.
- Die Verteilung erfolgt proportional über die gesamte Laufzeit:  
  `Monatsanteil = Vertragsbetrag / Anzahl der aktiven Monate (inklusiv Start/Ende)`.
- Verlauf wird als Monat-Balkendiagramm (Timeline) angezeigt.
- Optional: später Soll-Ist-Vergleich mit Ist-Buchungskosten.

### UI-Layout (Umgesetzt)
- Im Dialog „Budgetverwaltung“ werden die Bereiche „Kunden“ und „Verträge“ verwendet.
- Feldnamen:
  - Budgetquelle: `Kunde`
  - Zeitraumbezeichnung: `Vertragstitel`
  - Zeitraum: `Beginn` / `Ende` als Datumsauswahl.
- Menü „Verwaltung“:
  - Aufruf der Standortverwaltung (Oncall-Locations) ist der erste Eintrag.
  - Aufruf der Budgetverwaltung ist der letzte Eintrag.
- Der Monatsverlauf wird als Balkendiagramm mit einem Balken pro Monat visualisiert.

---

## Auslöser

- Admin öffnet Dialog/Modul „Budgetverwaltung“.
- Admin aktualisiert oder ergänzt Budgetdaten.
- Admin öffnet Verlaufsansicht zur Zeitbewertung.

---

## Akzeptanzkriterien

- Budgetquelle und -periode sind CRUD-fähig erfasst.
- Eingaben mit ungültigen Zeiträumen werden abgelehnt mit klarer Fehlermeldung.
- Offen-Ende-Budgets werden korrekt angezeigt.
- Zeitraumende ist verpflichtend; offene Enddaten werden nicht mehr unterstützt.
- Gesamtbudget wird für einen gewählten Zeitraum korrekt aggregiert (monatliche Sicht vorhanden).
- Die Oberfläche zeigt nachvollziehbar, welcher Zeitraum welchen Betrag beiträgt.

---

## Nicht-Ziele (MVP)

- Kein mehrstufiger Genehmigungsworkflow.
- Keine automatische Forecast- oder Forecast-to-budget-Optimierung.
- Kein hartes Sperren bei überlappenden Budgets derselben Quelle.

---

## Technischer Entwurf (vorläufig)

- Neue Entitäten/Tabellen:
  - `budget_source`
  - `budget_period`
- Service-/Repository-Schicht:
  - Erfassung, Update, Delete, Timeline-Berechnung
- Anwendungsservice:
  - Datenbereitstellung für Verwaltungsdialog
  - Berechnung der zeitlichen Summen
- UI:
  - Verwaltungsdialog
  - Verlauf/Monatssicht
