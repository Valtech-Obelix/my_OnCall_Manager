# my_OnCall_Manager - Übergabe als Python-unabhängige Anwendung

## Ziel
Der Kollege soll die Anwendung ohne lokale Python-Installation nutzen können.

## Build (macOS)
Im Projektverzeichnis:

```bash
./scripts/build_release.sh
```

Ergebnis:
- App-Bundle: `dist/my_OnCall_Manager.app`
- Zip für Weitergabe: `dist/my_OnCall_Manager-macOS.zip`

## Was weitergegeben wird
- `dist/my_OnCall_Manager-macOS.zip` (empfohlen) oder `dist/my_OnCall_Manager.app`
- optional `docs/README_Uebergabe.md` als Betriebsnotiz

## Daten- und Log-Pfade beim Kollegen
Die Anwendung schreibt nicht in das `.app`-Bundle, sondern in das Benutzerverzeichnis.

macOS:
- Datenbank: `~/Library/Application Support/my_OnCall_Manager/my_oncall_manager.db`
- Log: `~/Library/Application Support/my_OnCall_Manager/my_oncall_manager.log`
- Sichtbares Buchungs-CSV-Verzeichnis (automatisch angelegt bei Bedarf):
  `~/Documents/my_OnCall_Manager/data`

### Seed-Datenbank bei Erststart
- Beim Build wird die Projektdatei `my_oncall_manager.db` in die App als Seed eingebunden.
- Beim **ersten Start** wird diese Seed-DB nach
  `~/Library/Application Support/my_OnCall_Manager/my_oncall_manager.db`
  kopiert, falls dort noch keine DB existiert.
- Existiert bereits eine DB im Zielpfad, wird sie **nicht** ueberschrieben.

## CSV-Dateien für UC-012
Die Anwendung sucht `*.csv` für den Vergleich in folgender Reihenfolge:
1. `MY_ONCALL_DATA_DIR` (falls gesetzt)
2. `~/Documents/my_OnCall_Manager/data`
3. `data` neben der ausführbaren Datei
4. `~/Library/Application Support/my_OnCall_Manager/data`
5. eingebundener `data`-Ordner im Bundle

Empfehlung für den Kollegen:
- CSV-Dateien nach `~/Documents/my_OnCall_Manager/data` legen.
- In der App kann der Ordner direkt über `Schichtplan -> CSV-Ordner öffnen`
  geöffnet werden.

## OpsGenie-Import aktivieren
Der Menüpunkt "OpsGenie Schichten importieren" ist nur aktiv, wenn
ein OpsGenie API-Key verfuegbar ist.

### Option A: Direkt per Umgebungsvariable

Temporär (nur aktuelles Terminal):

```bash
export OPS_GENIE_API_KEY="<dein-key>"
open dist/my_OnCall_Manager.app
```

### Option B: Bezug aus 1Password (empfohlen)

Voraussetzungen:
- 1Password CLI `op` ist installiert
- Der Benutzer ist am `op`-CLI angemeldet

Dann nur die Referenz setzen (der eigentliche Key bleibt in 1Password):

```bash
export OPS_GENIE_API_KEY_OP_REF="op://<Vault>/<Item>/<Feld>"
open dist/my_OnCall_Manager.app
```

Beispiel:

```bash
export OPS_GENIE_API_KEY_OP_REF="op://Shared/OpsGenie/api_key"
open dist/my_OnCall_Manager.app
```

Die App versucht zuerst `OPS_GENIE_API_KEY`, danach `OPS_GENIE_API_KEY_OP_REF`
ueber `op read`.

## Plattformhinweis
PyInstaller-Builds sind plattformspezifisch:
- macOS-Build läuft auf macOS
- Windows-Build muss auf Windows erstellt werden
