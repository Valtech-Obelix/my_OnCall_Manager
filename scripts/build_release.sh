#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
if [[ ! -x "${PYTHON_BIN}" ]]; then
  echo "Python interpreter not found at '${PYTHON_BIN}'."
  echo "Set PYTHON_BIN or create .venv first."
  exit 1
fi

echo "Building release with PyInstaller..."
"${PYTHON_BIN}" -m PyInstaller my_OnCall_Manager.spec --clean -y

APP_PATH="dist/my_OnCall_Manager.app"
ZIP_PATH="dist/my_OnCall_Manager-macOS.zip"
if [[ -d "${APP_PATH}" ]]; then
  echo "Creating zip archive..."
  ditto -c -k --sequesterRsrc --keepParent "${APP_PATH}" "${ZIP_PATH}"
fi

echo "Done."
echo "App: ${APP_PATH}"
echo "Zip: ${ZIP_PATH}"
