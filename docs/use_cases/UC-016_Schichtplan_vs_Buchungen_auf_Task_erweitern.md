# UC-016 – Schichtplan-vs.-Buchungen um Task-Prüfung erweitern

## Version
0.1

---

## Ziel

Als Administrator  
möchte ich beim Vergleich zwischen Schichtplan und Buchungen zusätzlich den gebuchten Task prüfen,  
um fachlich falsche Buchungen auch dann zu erkennen, wenn IA, Tag und Schichtslot korrekt sind.

---

## Hauptablauf

1. Administrator öffnet den Dialog „Schichtplan vs. Buchungen vergleichen“.
2. Administrator wählt Schichtplan und Wochenstart.
3. System lädt Soll-Schichten (OpsGenie) und Ist-Buchungen (CSV).
4. System prüft pro Tag/Slot:
   - IA-Übereinstimmung zwischen Plan und Buchung
   - erwarteten Task je IA-Standort, Tagtyp und Slot
5. System markiert die Buchung als:
   - korrekt (grün), wenn IA/Anzahl und Task-Regel erfüllt sind
   - fehlerhaft (orange), wenn mindestens eine Regel verletzt ist
6. System zeigt im Tooltip den konkreten Fehlergrund.

---

## Task-Regeln

### Standort `GER`
- Werktag (Mo-Fr), Slot `F` und `S`: `Rufbereitschaft Werktags`
- Werktag (Mo-Fr), Slot `T`: keine Buchung erlaubt
- Samstag (`Sa`), alle Slots: `Rufbereitschaft Samstags und Betriebsurlaub`
- Sonntag oder Feiertag, alle Slots: `Rufbereitschaft Sonn- und Feiertags`

### Standort `IND`
- Werktag (Mo-Fr), alle Slots: `On Call Shift Working days`
- Wochenende (`Sa` + `So`) oder Feiertag, alle Slots: `On Call Shift Weekend and Holidays`

---

## Akzeptanzkriterien

- Eine Buchung mit korrektem IA, Datum und Slot wird als fehlerhaft markiert, wenn der Task nicht der Regel entspricht.
- Für `GER` wird am Werktag im Slot `T` jede vorhandene Buchung als fehlerhaft markiert.
- Bei fehlerhaften Buchungen ist der Fehlergrund im Tooltip unterscheidbar.
- Bestehende IA-/Slot-Abweichungen bleiben weiterhin als Fehler sichtbar.
