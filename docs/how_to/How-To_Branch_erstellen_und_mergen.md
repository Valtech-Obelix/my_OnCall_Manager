# How-To: Branch erstellen und mergen

## 1. Neuen Branch erstellen

```bash
git fetch origin
git switch main
git pull origin main
git switch -c feature/<kurzer-name>
git push -u origin feature/<kurzer-name>
```

Beispiel:

```bash
git switch -c feature/UC-012-release-handover
git push -u origin feature/UC-012-release-handover
```

## 2. Auf dem Branch arbeiten

```bash
git add .
git commit -m "UC-012: <kurze beschreibung>"
git push
```

## 3. Branch in `main` mergen

```bash
git fetch origin
git switch main
git pull origin main
git merge --no-ff feature/<kurzer-name>
git push origin main
```

## 4. Branch aufraeumen (optional)

```bash
git branch -d feature/<kurzer-name>
git push origin --delete feature/<kurzer-name>
```

## Typische Fehler

### Fehler: `MERGE_HEAD existiert`

Es ist noch ein alter Merge offen.

```bash
git status
git merge --abort
```

Danach Merge erneut starten.

### Merge-Editor (vim) oeffnet sich

Wenn diese Datei erscheint (`MERGE_MSG`):

1. `i` druecken
2. Commit-Text oben schreiben
3. `Esc`
4. `:wq` + `Enter`

Abbrechen:

1. `Esc`
2. `:q!` + `Enter`
