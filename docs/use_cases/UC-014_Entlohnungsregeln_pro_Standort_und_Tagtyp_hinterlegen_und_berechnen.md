# UC-014 – Entlohnungsregeln pro Standort und Tagtyp hinterlegen und berechnen

## Version
0.1

---

## Ziel

Als Admin  
möchte ich Entlohnungsregeln pro Standort und Tagtyp hinterlegen und automatisiert berechnen können,  
um monatliche Auszahlungen korrekt vorbereiten zu können.

---

## Hauptablauf

1. System erhält eine Schicht mit Standort und Startzeit.
2. System ermittelt den Schichttyp (`F`, `T`, `S`).
3. System bestimmt den Tagtyp (`Werktag`, `Samstag`, `Sonntag/Feiertag`).
4. System ermittelt den Entlohnungsbetrag gemäß Standortregel.
5. System liefert den Betrag pro Schicht zurück.

---

## Akzeptanzkriterien

- Entlohnungslogik für `GER`:
  - Werktag: `F=125`, `T=0`, `S=125`
  - Samstag: `F/T/S=150`
  - Sonntag/Feiertag (Bayern): `F/T/S=180`
- Entlohnungslogik für `IND`:
  - Werktag: `F/T/S=6`
  - Samstag/Sonntag/Feiertag: `F/T/S=10`
- Feiertagserkennung basiert auf bayerischen Feiertagen.
- Für unbekannte Standorte wird ein fachlicher Fehler zurückgegeben.
