# CR-035 – App-Version in UI anzeigen und Git-Metadaten im Über-Dialog

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-03-07
- Umgesetzt am: 2026-03-07
- Anforderer: Entwicklung / Release
- Betroffener Use Case: UC-023

## Beschreibung (fachlich)

Die Anwendung soll die aktuelle Software-Version im Hauptfenster anzeigen und im
`Über my_OnCall_Manager`-Dialog die Build-Metadaten anzeigen, damit Anwender und
Support schnell nachvollziehen können, mit welcher Version die App läuft.

## Anforderungen

- Version ist im Fenster-Titel enthalten (z. B. `my_OnCall_Manager v1.0.1`).
- Untertitel im Dashboard zeigt die Version ebenfalls an.
- Ein neuer Menüpunkt `Über my_OnCall_Manager` öffnet einen Dialog mit:
  - Version
  - Commit-ID (falls verfügbar)
  - Build-Datum (falls verfügbar)
- Die Versionsnummer basiert auf Git-Tags im Repo (`git describe ...`).
- Bei fehlenden Git-Daten läuft die Darstellung als Fallback auf `dev`.
- Dokumentation ist im Übergabe-How-To ergänzt.

## Technische Umsetzung

- Neue Moduldatei `src/infrastructure/app_version.py`:
  - `get_app_version()` liest zuerst Umgebungsvariablen (`MY_ONCALL_MANAGER_VERSION`,
    `APP_VERSION`) und fällt anschließend auf `git describe --tags --dirty --always` zurück.
  - `get_app_build_info()` liefert Dict mit `version`, optional `commit` und `build_time`.
- `src/ui/main_window.py`:
  - Titel/Subtitle mit Versionsanzeige ergänzt.
  - Menüpunkt `Über my_OnCall_Manager` ergänzt.
  - Neuer Dialog zeigt Versionsinformationen aus `get_app_build_info()`.
- `docs/how_to/README_Uebergabe.md` um die neue Config-basierte OpsGenie-Initialisierung ergänzt.
- Build/Release-Tag bleibt der alleinige primäre Ursprung der Version.

## Betroffene Dateien

- `src/infrastructure/app_version.py`
- `src/ui/main_window.py`
- `docs/how_to/README_Uebergabe.md`
- `docs/use_cases/00_UseCase_Index.md`

## Akzeptanzkriterien

- Hauptfenster zeigt die Version im Titel.
- `Über my_OnCall_Manager`-Dialog ist verfügbar und zeigt die erwarteten Werte.
- Bei Tag `v1.0.1` auf Commit-Ebene wird genau diese Version angezeigt.
- Im Frozen-Build wird die App weiterhin lauffähig, auch wenn Git-Informationen fehlen (Fallback auf `dev`).
