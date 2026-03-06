# UC-020 – Buchungen Kosten zuordnen

## Version
0.2

---

## Ziel

Als Administrator  
möchte ich Buchungen je Tasktyp kostenmäßig auswerten können,  
um den Budgetverbrauch pro Monat standortbezogen nachvollziehen zu können.

---

## Vorbedingungen

- Incident-Analysten mit gültigem Buchungsnamen sind vorhanden.
- Gehaltsgruppen und Zuordnungen mit historisierten Beträgen sind gepflegt.
- Standortdaten (`GER`, `IND`) sind vorhanden.
- Buchungsdaten liegen als CSV mit Kopfzeile und Spalten `Date`, `User`, `Task - Task type`, `Task`, `Notes`, `Time (Hours)` vor.
- Datumsformat in CSV ist `DD-MM-YY`.

---

## Auslöser / Einstieg

- Aus der Menüleiste:
  - `Auswertung → Client Utilized Kosten testen`
  - `Auswertung → Overtime Kosten testen`
  - `Auswertung → On Call Kosten testen`
- Der Anwender wählt Jahr, Monat und Standortfilter.

---

## Hauptablauf

1. Anwender öffnet den entsprechenden Testdialog.
2. Anwender wählt Jahr, Monat und Standort.
3. System lädt Buchungen des Filtersatzes.
4. Für jeden Datensatz werden Betrag/Anteil/Status berechnet.
5. Tabelle und berechnete Gesamtsumme werden angezeigt.

---

## Regelwerk

### Client Utilized

- Relevante Buchungen: `Task - Task type = Client Utilized`.
- Pro Kombination aus Datum, Analyst und Task werden Stunden kumuliert.
- Zuordnung Analyst erfolgt über Buchungsname.
- Für den Buchungszeitpunkt wird das gültige Gehaltsgruppen-Datum ermittelt.
- Berechnung:
  - `Kosten = Gehaltsgruppe_Betrag * Stunden`
- Bei fehlendem Mitarbeiter, fehlender Gehaltsgruppe oder fehlendem Betrag: `Kosten = 0`, Fehlertext in `Status`.
- Anzeige: Datum, Buchungsname, Task, Stunden, Stundensatz, Kosten, Gehaltsgruppe, Gehaltsgruppenbetrag, Status.

### Overtime

- Relevante Tasks:
  - `Arbeit (25%) WT (6-9, 17-20) Sa (6-20)`
  - `Arbeit (50%) WT (20-6), Sa (20-6), So & FT`
  - `Work On Call Shift (Mo-Sat)`
  - `Work On Call Shift (Sunday)`
- Pro Kombination aus Datum, Analyst, Task werden:
  - Stunden summiert
  - `booking_count` als Buchungsanzahl gezählt
- Berechnung:
  - `Task Arbeit (25%) ...` → `Kosten = Gehaltsgruppe_Betrag * Stunden * 1,25`
  - `Task Arbeit (50%) ...` → `Kosten = Gehaltsgruppe_Betrag * Stunden * 1,5`
  - `Work On Call Shift (Mo-Sat)` → `Kosten = 10 * booking_count`
  - `Work On Call Shift (Sunday)` → `Kosten = 10 * booking_count`
- Fehlerfälle analog Client Utilized; unbekannte Overtime-Tasks werden mit Status `Unbekannter Overtime Task` auf `0` gesetzt.
- Anzeige: Datum, Buchungsname, Task, Stunden, Stundensatz, Kosten, Gehaltsgruppe, Gehaltsgruppenbetrag, Status.

### On Call

- Relevante Buchungen: `Task - Task type = On Call`.
- Slot wird aus `Notes` bestimmt:
  - Früh `F`, Tag `T`, Spät `S`
- `Time (Hours)` wird als Einheiten geladen; jede Einheit wird intern zu einer Ergebniszeile (`Einheiten = 1`) aufgelöst.

- Deutschland (`GER`):
  - Basisrate aus Entlohnungslogik für Tag/Slot.
  - `Lohnnebenkosten = 25% der Basisrate`
  - `Kosten = Basisrate + Lohnnebenkosten`
  - Tabelle: Buchungsdatum, Buchungsname, Task, Slot, Einheiten, Stundensatz, Lohnnebenkosten, Kosten

- Indien (`IND`):
  - Gehaltsgruppenbetrag am Buchungsdatum wird ermittelt.
  - `Schichtbasispreis = 6`
  - `Arbeitszeitausgleich = Gehaltsgruppenbetrag * 4`, nur bei Sa/So/Feiertag.
  - `Kosten = Schichtbasispreis + Arbeitszeitausgleich`
  - Tabelle: Buchungsdatum, Buchungsname, Task, Slot, Gehaltsgruppenbetrag, Einheiten, Schichtbasispreis, Arbeitszeitausgleich, Kosten
- Für On-Call wird keine Statusspalte angezeigt.

---

## Ausnahmen

- Analyst nicht gefunden: `Mitarbeiter nicht gefunden`.
- Standortfilter passt nicht: Zeile wird nicht angezeigt.
- On-Call-Buchung mit ungültigem Slot/Zeiteintrag: `Ungültiger Buchungseintrag`.
- Kein gültiger Betrag am Stichtag:
  - `Keine Gehaltsgruppe am Buchungsdatum`
  - `Kein Betrag für diesen Tag ...`

---

## Technische Hinweise

- Betroffene Module
  - `src/services/compensation_service.py`
    - Taskklassifizierung Overtime
    - Overtime/Client/On-Call Laden
    - Feiertags-/Wochentagslogik
  - `src/app/application.py`
    - `get_client_utilized_costs_for_month`
    - `get_overtime_costs_for_month`
    - `get_on_call_costs_for_month`
  - `src/ui/client_utilized_cost_dialog.py`
  - `src/ui/overtime_cost_dialog.py`
  - `src/ui/on_call_cost_dialog.py`
  - `src/ui/main_window.py`

---

## Akzeptanzkriterien

- Die drei Testdialoge sind über das Menü erreichbar und lauffähig.
- Für jeden Standortfilter werden nur zugehörige Datensätze angezeigt.
- Overtime erkennt und berechnet alle vier fachlichen Tasks.
- On-Call nutzt bei `GER`/`IND` unterschiedliche Tabellen- und Kostenlogik.
- Bei Datenmängeln sind Ursachen im Status ersichtlich und werden nicht stillschweigend als korrekte Nullkosten behandelt.
