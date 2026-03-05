#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PORT="${PORT:-5000}"
WORKERS="${WORKERS:-2}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 not found."
  exit 1
fi

python3 -m pip install -r requirements.txt

echo "Starting backend on 0.0.0.0:${PORT} with ${WORKERS} workers..."
exec gunicorn -w "${WORKERS}" -b "0.0.0.0:${PORT}" app:app
