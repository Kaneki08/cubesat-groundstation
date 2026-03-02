#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_DIR="$ROOT_DIR/server"
UI_DIR="$ROOT_DIR/ui"

if [[ ! -x "$SERVER_DIR/venv/bin/fastapi" ]]; then
  echo "[backend] Missing FastAPI CLI in server venv."
  echo "Run: cd server && source venv/bin/activate && pip install -r requirements.txt \"fastapi[standard]\""
  exit 1
fi

if [[ ! -f "$UI_DIR/package.json" ]]; then
  echo "[ui] Missing package.json in ui/."
  exit 1
fi

if [[ ! -d "$UI_DIR/node_modules" ]]; then
  echo "[ui] node_modules not found. Running npm install..."
  (cd "$UI_DIR" && npm install)
fi

echo "[ui] Building UI for single-port serving..."
(cd "$UI_DIR" && npm run build)

echo "[backend] Starting FastAPI + UI on http://127.0.0.1:8000"
cd "$SERVER_DIR"
exec ./venv/bin/fastapi run app_fastapi.py --host 0.0.0.0 --port 8000
