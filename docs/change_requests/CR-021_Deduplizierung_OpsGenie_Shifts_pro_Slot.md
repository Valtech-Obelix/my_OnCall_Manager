# CR-021 – Deduplizierung von OpsGenie-Schichten pro Slot (inkl. Altbestand)

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-03-02
- Umgesetzt am: 2026-03-02
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-004, UC-012

## Beschreibung (fachlich)

Im Schichtplan wurden vereinzelt doppelte Einträge für denselben Mitarbeiter im
gleichen Schicht-Slot angezeigt (z. B. mit 1-Sekunden-Abweichung in der Startzeit).
Diese Duplikate sollen beim Import nicht mehr übernommen werden.
Zusätzlich soll der bestehende Datenbestand bereinigt werden.

## Akzeptanzkriterien

- Pro `Schedule + Mitarbeiter + Kalendertag + Schichtslot (Früh/Tag/Spät)` wird
  maximal eine Schicht gespeichert.
- OpsGenie-Import ignoriert zeitnahe Duplikate im selben Slot.
- Bestehende Duplikate in `shifts` können einmalig bereinigt werden.
- Tagesansichten zeigen keine künstlichen `(2x)`-Dubletten mehr für denselben Slot.

## Technische Umsetzung

- Importlogik in `OpsGenieService` um slotbasierte Schlüsselbildung erweitert.
- Bereits vorhandene Schichten werden vor Import als Slot-Schlüssel geladen.
- Beim Import werden Perioden mit identischem Slot-Schlüssel als Duplikat geskippt.
- `ShiftRepository` um Methode für bestehende Startzeiten pro Schedule ergänzt.
- Bestandsdaten einmalig per Bereinigungsskript dedupliziert
  (ältesten Datensatz pro Slot behalten).

## Betroffene Dateien

- `src/services/opsgenie_service.py`
- `src/infrastructure/shift_repository.py`

## Tests / Validierung

- `python3 -m compileall -q src`
- Manuelle DB-Prüfung auf entfernte Slot-Duplikate in `shifts`

