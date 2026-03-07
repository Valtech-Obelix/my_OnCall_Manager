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

### Release-Verantwortung: dist aktualisieren

Nach jeder funktionalen Änderung **immer** neu bauen, damit die verteilte ZIP die aktuelle
Version enthält.

```bash
./scripts/build_release.sh
```

Prüfen nach dem Build:
- Neue `dist/my_OnCall_Manager-macOS.zip` im Ausgabeordner
- Inhalt enthält die aktuellen Dateien aus `dist/my_OnCall_Manager.app` sowie den aktuellen
  Start-Wrapper `dist/my_OnCall_Manager.command`
- Versionsanzeige beim Appstart stimmt (z. B. mit `Über my_OnCall_Manager` und Log-Header)

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

Die Konfiguration erfolgt über die App-Config-Datei:

```bash
open dist/my_OnCall_Manager.app
```

Die App liest dazu die Datei:

```bash
~/Library/Application Support/my_OnCall_Manager/opsgenie_config.json
```

Falls die Datei nicht vorhanden ist, kannst du stattdessen die mitgelieferte
Beispiel-Datei `opsgenie_config.example.json` im Projekt nutzen (z. B. nach
`opsgenie_config.json` kopieren und die Referenz anpassen):

```bash
cp opsgenie_config.example.json ~/Library/Application Support/my_OnCall_Manager/opsgenie_config.json
```

Mit folgendem Inhalt:

```json
{
  "opsgenie": {
    "api_key_reference": "op://<Vault>/<Item>/<Feld>"
  }
}
```

Beispiel:

```json
{
  "opsgenie": {
    "api_key_reference": "op://Shared/OpsGenie/api_key"
  }
}
```

Damit bleibt der eigentliche Schlüssel in 1Password.

Die App liest die Referenz aus `~/Library/Application Support/my_OnCall_Manager/opsgenie_config.json` via `op read`.

## 1Password-CLI einrichten

Voraussetzung für den automatischen Abruf aus `op://...` ist eine funktionierende 1Password-CLI-Sitzung auf dem Zielrechner.

Einmalig pro Rechner (oder nach neuem Nutzerkonto):

1. CLI installieren (falls noch nicht vorhanden):

```bash
brew install --cask 1password-cli
```

2. App-Integration in 1Password aktivieren (empfohlen):
   - In der 1Password Desktop-App die Einstellungen öffnen
   - Bereich **Entwickler** (Developer) aktivieren/integrieren
   - Sicherstellen, dass der angemeldete Account für die CLI freigegeben ist

3. Einmalig ein Konto anmelden:

```bash
op signin
```

4. Prüfung (muss auf dem Zielsystem im Startkontext funktionieren):

```bash
op account list
op read "op://<Vault>/<Item>/<Feld>"
```

Wenn der Import in der Distribution nicht funktioniert, liegt in der Regel das CLI-Umfeld im App-Prozess nicht vor. In diesem Fall App über ein Terminal mit bestehender `op`-Sitzung starten.

## Start der App mit funktionierender 1Password-Session (macOS)

Falls im `.app`-Bundle weiterhin `No accounts configured for use with 1Password CLI` erscheint, ist die 1Password-Sitzung im App-Prozesskontext in der Regel nicht verfügbar.

Starte die App dann direkt über `op run` aus einem Terminal, in dem die 1Password-CLI funktioniert:

```bash
./scripts/start_dist_with_op.sh
```

Das Wrapper-Skript startet direkt das App-Binary im `op run`-Kontext und hält damit die temporäre CLI-Sitzung für den Prozess.

### Empfohlener Verteiler-Weg

Das Build erzeugt zusätzlich:

- `dist/my_OnCall_Manager.command`

Diese Datei ist für Kolleg:innen gedacht, die keinen eigenen Dev-Workflow nutzen.  
Sie startet die App im `op run`-Kontext ohne `python3 main.py`:

```bash
open dist/my_OnCall_Manager.command
```

oder Doppelklick auf die Datei.

### Voraussetzungen
- 1Password CLI `op` ist installiert
- Der Benutzer ist am `op`-CLI angemeldet
- Wenn die App aus dem `.app`-Bundle gestartet wird (Finder/Launchpad), muss die 1Password-Sitzung ebenfalls im Prozesskontext vorhanden sein.
  In einigen Umgebungen zeigt `op read` sonst `No accounts configured for use with 1Password CLI`.
  Abhilfe: App einmalig aus einem Terminal starten, in dem `op signin` bereits ausgeführt wurde, oder `op` mit einem Service-Account-Token (`OP_SERVICE_ACCOUNT_TOKEN`) ausführen.

Die App liest die Referenz aus der Datei via `op read`.

## Plattformhinweis
PyInstaller-Builds sind plattformspezifisch:
- macOS-Build läuft auf macOS
- Windows-Build muss auf Windows erstellt werden
