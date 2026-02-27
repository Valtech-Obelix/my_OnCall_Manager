# UC-006 – Erstimport eines Schichtplans ab Jahresbeginn

## Version
0.2

---

## Ziel

Als Administrator  
möchte ich beim erstmaligen Abruf eines Schichtplans alle Schichten ab dem 01.01. des aktuellen Jahres importieren,  
um alle Schichten eines Jahres verwalten zu können.

---

## Fachliche Regel

- Wenn ein Schichtplan (`Schedule ID`) zum ersten Mal importiert wird:
  - Import mit Zeitfenster ab Jahresbeginn:
    - `since = 01.01.<aktuelles Jahr> 00:00:00Z`
    - `until = 31.12.<aktuelles Jahr> 23:59:59Z`
    - `date = 01.01.<aktuelles Jahr> 00:00:00Z`
    - `interval = 12`, `intervalUnit = months`
- Wenn der Schichtplan bereits mindestens einmal importiert wurde:
  - Import ohne erzwungenes Jahresfenster (bisheriges Verhalten)

---

## Zeitzonenregel

- Schichtzeiten werden technisch in UTC (`...Z`) gespeichert.
- Die Anzeige des importierten Gesamtzeitraums erfolgt in `Europe/Berlin` und berücksichtigt Sommer-/Winterzeit (CET/CEST).

---

## Betroffene Komponenten

- Service: `src/services/opsgenie_service.py`
- Repository: `src/infrastructure/shift_repository.py`
- Integration: `src/infrastructure/opsgenie_client.py`
- Zeitzone: `src/infrastructure/timezone_utils.py`
- Tests: `tests/test_opsgenie_service.py`, `tests/test_shift_repository.py`, `tests/test_timezone_utils.py`
