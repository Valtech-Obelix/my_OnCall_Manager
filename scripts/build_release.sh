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
if [[ -d "${APP_PATH}" ]]; then
  plutil -replace CFBundleShortVersionString -string "${APP_VERSION}" "${APP_PATH}/Contents/Info.plist"
  plutil -replace CFBundleVersion -string "${APP_VERSION}" "${APP_PATH}/Contents/Info.plist"
  plutil -replace MyOnCallManagerBuildDate -string "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" "${APP_PATH}/Contents/Info.plist"
  plutil -replace MyOnCallManagerBuildCommit -string "$(git -C "${ROOT_DIR}" rev-parse --short HEAD 2>/dev/null || true)" "${APP_PATH}/Contents/Info.plist"

  echo "Creating zip archive..."
  ditto -c -k --sequesterRsrc --keepParent "${APP_PATH}" "${VERSIONED_ZIP_PATH}"
  cp "${VERSIONED_ZIP_PATH}" "${ZIP_PATH}"
fi

echo "Done."
echo "App: ${APP_PATH}"
echo "Zip: ${VERSIONED_ZIP_PATH}"
