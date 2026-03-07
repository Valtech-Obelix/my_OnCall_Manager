#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

APP_VERSION_TAG="${MY_ONCALL_MANAGER_VERSION:-}"
if [[ -z "${APP_VERSION_TAG}" ]]; then
  APP_VERSION_TAG="$(git -C "${ROOT_DIR}" describe --tags --abbrev=0 2>/dev/null || true)"
  if [[ -z "${APP_VERSION_TAG}" ]]; then
    APP_VERSION_TAG="$(git -C "${ROOT_DIR}" describe --always --dirty --abbrev=7 2>/dev/null || true)"
  fi
fi
APP_VERSION_TAG="${APP_VERSION_TAG%%-*}"
APP_VERSION="${APP_VERSION_TAG#v}"
if [[ -z "${APP_VERSION}" ]]; then
  APP_VERSION="0.0.0"
fi

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
if [[ ! -x "${PYTHON_BIN}" ]]; then
  echo "Python interpreter not found at '${PYTHON_BIN}'."
  echo "Set PYTHON_BIN or create .venv first."
  exit 1
fi

echo "Building release with PyInstaller..."
"${PYTHON_BIN}" -m PyInstaller my_OnCall_Manager.spec --clean -y

APP_PATH="dist/my_OnCall_Manager.app"
VERSIONED_ZIP_PATH="dist/my_OnCall_Manager-${APP_VERSION_TAG}-macOS.zip"
ZIP_PATH="dist/my_OnCall_Manager-macOS.zip"
COMMAND_STUB_PATH="dist/my_OnCall_Manager.command"
README_PATH="dist/README-macOS-Start.txt"
if [[ -d "${APP_PATH}" ]]; then
  plutil -replace CFBundleShortVersionString -string "${APP_VERSION}" "${APP_PATH}/Contents/Info.plist"
  plutil -replace CFBundleVersion -string "${APP_VERSION}" "${APP_PATH}/Contents/Info.plist"
  plutil -replace MyOnCallManagerBuildDate -string "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" "${APP_PATH}/Contents/Info.plist"
  plutil -replace MyOnCallManagerBuildCommit -string "$(git -C "${ROOT_DIR}" rev-parse --short HEAD 2>/dev/null || true)" "${APP_PATH}/Contents/Info.plist"

  cat > "${COMMAND_STUB_PATH}" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_BIN="${SCRIPT_DIR}/my_OnCall_Manager.app/Contents/MacOS/my_OnCall_Manager"

if [[ ! -x "${APP_BIN}" ]]; then
  echo "MyOnCall app binary not found or not executable: ${APP_BIN}"
  exit 1
fi

if ! command -v op >/dev/null 2>&1; then
  echo "1Password CLI (op) not found in PATH."
  echo "Please install 1Password CLI and start 1Password desktop app integration."
  exit 1
fi

  echo "Starting my_OnCall_Manager with 1Password CLI context..."
  op run -- "${APP_BIN}"
EOF
  chmod +x "${COMMAND_STUB_PATH}"

  cat > "${README_PATH}" <<'EOF'
my_OnCall_Manager – macOS Distribution
=====================================

So starten Sie die App korrekt:

1. Installieren Sie 1Password und aktivieren Sie die CLI-Integration.
2. Stellen Sie sicher, dass `op` im Terminal funktioniert:

   op read 'op://BC-SPORT.Team-Evoli/OpsGenie_API_my_OnCall_Manager/API_KEY'

3. Starten Sie die App über den mitgelieferten Launcher:

   open my_OnCall_Manager.command

oder per Doppelklick auf die Datei `my_OnCall_Manager.command`.

Wichtig:
- Der Menüeintrag „OpsGenie Schichten importieren“ ist nur aktiv, wenn der API-Key in 1Password lesbar ist.
- Bitte die Datei `~/Library/Application Support/my_OnCall_Manager/opsgenie_config.json` anlegen/prüfen und die Referenz eintragen.
  - Optional: Kopieren Sie die mitgelieferte Beispielkonfiguration aus dem Projekt `opsgenie_config.example.json` nach
   `~/Library/Application Support/my_OnCall_Manager/opsgenie_config.json`.

EOF

  echo "Creating zip archive..."
  cd dist
  /usr/bin/zip -qr "../${VERSIONED_ZIP_PATH}" "my_OnCall_Manager.app" "my_OnCall_Manager.command" "README-macOS-Start.txt"
  cd "${ROOT_DIR}"
  cp "${VERSIONED_ZIP_PATH}" "${ZIP_PATH}"
fi

echo "Done."
echo "App: ${APP_PATH}"
echo "Zip: ${VERSIONED_ZIP_PATH}"
echo "Launcher: ${COMMAND_STUB_PATH}"
echo "Readme: ${README_PATH}"
