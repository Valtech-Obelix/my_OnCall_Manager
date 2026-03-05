# UC-018 – Einfuehrung von Mitarbeitertypen

## Version
0.1

---

## Ziel

Als Administrator  
moechte ich neben Incident Analysts auch andere Mitarbeiter (z. B. Product Owner) verwalten koennen,  
um alle relevanten Personen zentral in der Mitarbeiterverwaltung pflegen zu koennen.

---

## Fachliche Erweiterung

Ein Mitarbeiter erhaelt ein neues Attribut:

- `Mitarbeitertyp`

Zulaessige Werte:

- `INCIDENT_ANALYST`
- `PRODUCT_OWNER`
- `SONSTIGE`

---

## Hauptablauf

1. Administrator oeffnet den Menuepunkt `der Mitarbeiter`.
2. System zeigt den Dialog `Mitarbeiterverwaltung`.
3. Administrator legt einen neuen Mitarbeiter an oder bearbeitet einen bestehenden.
4. Administrator waehlt den `Mitarbeitertyp` aus.
5. System speichert den Mitarbeiter inklusive Mitarbeitertyp.

---

## Akzeptanzkriterien

- Menuepunkt ist von `Incident Analysten verwalten` auf `der Mitarbeiter` umbenannt.
- Dialogtitel ist von `Verwaltung der Incident Analysten` auf `Mitarbeiterverwaltung` umbenannt.
- Im Dialog ist `Mitarbeitertyp` als editierbares Feld vorhanden.
- `Mitarbeitertyp` wird in der Tabelle angezeigt.
- Bestehende Datensaetze erhalten automatisch den Default `INCIDENT_ANALYST`.

---

## Zugehoerige Change Requests

- [CR-028 – Mitarbeitertyp im Mitarbeiterdialog und Datenmodell](../change_requests/CR-028_Mitarbeitertyp_im_Mitarbeiterdialog_und_Datenmodell.md)
