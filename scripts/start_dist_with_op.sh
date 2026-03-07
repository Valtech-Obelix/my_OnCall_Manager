#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_BIN="${SCRIPT_DIR}/../dist/my_OnCall_Manager.app/Contents/MacOS/my_OnCall_Manager"

if [[ ! -x "${APP_BIN}" ]]; then
  echo "MyOnCall app binary not found or not executable: ${APP_BIN}"
  echo "Run ./scripts/build_release.sh first."
  exit 1
fi

if ! command -v op >/dev/null 2>&1; then
  echo "1Password CLI (op) not found."
  exit 1
fi

echo "Starting my_OnCall_Manager with 1Password CLI session context..."
op run -- "${APP_BIN}"
