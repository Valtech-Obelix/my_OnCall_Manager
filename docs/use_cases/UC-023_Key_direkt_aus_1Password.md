# UC-023 – OpsGenie API-Key direkt aus 1Password via Config lesen

## Version
0.1

---

## Ziel

Als Admin
möchte ich den OpsGenie API-Key ausschließlich über eine 1Password-Referenz laden,
ohne den Key in Umgebungsvariablen hinterlegen zu müssen,
damit der Abruf der Schichten sicher und ohne lokale Schlüsselhaltung erfolgt.

---

## Hintergrund

Der aktuelle Stand liest den Schlüssel bisher aus Umgebungsvariablen (`OPS_GENIE_API_KEY`)
oder indirekt über `OPS_GENIE_API_KEY_OP_REF`.
Beides erfordert eine env-Basierte Konfiguration.
Mit dieser Änderung wird ausschließlich die 1Password-Referenz aus einer
Config-Datei im App-Datenverzeichnis gelesen.

---

## Konfiguration

- Datei: `<App-Datenverzeichnis>/opsgenie_config.json`
- Erwarteter Inhalt:

```json
{
  "opsgenie": {
    "api_key_reference": "op://Shared/OpsGenie/api_key"
  }
}
```

- Der API-Key selbst liegt weiterhin in 1Password.
- Die App nutzt `op read <referenz>`, um den Schlüssel zur Laufzeit zu lesen.

---

## Vorbedingungen

- 1Password CLI (`op`) ist installiert.
- Die User-Sitzung von `op` ist aktiv.
- Die Datei `opsgenie_config.json` im App-Datenverzeichnis ist vorhanden und korrekt gefüllt.

---

## Sollzustand

1. Die Anwendung liest beim Start `opsgenie_config.json`.
2. Aus dem Feld `opsgenie.api_key_reference` wird die 1Password-Referenz geladen.
3. Die App ruft die Referenz mit `op read` ab und erzeugt den OpsGenie-Client.
4. Bei Fehlern (fehlende Datei, ungültiges JSON, fehlende Referenz, `op` nicht verfügbar,
   Lesefehler) wird der Import als deaktiviert markiert und eine verständliche Warnung geloggt.
5. Es wird kein API-Key via Umgebungsvariable ausgelesen.

---

## Akzeptanzkriterien

- Der OpsGenie Import funktioniert ohne `OPS_GENIE_API_KEY`.
- Der Import funktioniert ohne `OPS_GENIE_API_KEY_OP_REF`.
- Der API-Key wird nur kurzzeitig in Arbeitsspeicher gehalten und nicht dauerhaft in der App gespeichert.
- Ohne gültige Config-Datei bleibt der Menüpunkt „OpsGenie Schichten importieren“ deaktiviert.
- Die Funktionalität ist dokumentiert.

---

## Offene Punkte

- Optional: ein kleinerer CLI-Indikator in der UI, falls 1Password nicht erreichbar ist.
- Optional: UI-Warnung in der OpsGenie-Importansicht anstelle nur des Loggings.
