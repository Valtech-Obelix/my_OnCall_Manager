# CR-029 – Benennung Menüpunkt Verwaltung im Genitiv

## Metadaten

- Status: umgesetzt
- Erstellt am: 2026-03-05
- Umgesetzt am: 2026-03-05
- Anforderer: Fachbereich / Product Owner
- Betroffener Use Case: UC-018

## Beschreibung (fachlich)

Im Menü `Verwaltung` sollen die Einträge sprachlich im Genitiv
angezeigt werden.

## Akzeptanzkriterien

- Menü zeigt `der Gehaltsgruppen`.
- Menü zeigt `der Mitarbeiter`.
- Menü zeigt `der Rufbereitschaftsstandorte`.

## Technische Umsetzung

- Textkonstanten der drei Menüeinträge im Hauptfenster angepasst.
- Use-Case-Dokumentation für UC-018 auf neue Beschriftung aktualisiert.

## Betroffene Dateien

- `src/ui/main_window.py`
- `docs/use_cases/UC-018_Einfuehrung_von_Mitarbeitertypen.md`
- `docs/change_requests/00_CR_Index.md`

## Tests / Validierung

- `.venv/bin/python -m py_compile src/ui/main_window.py`
