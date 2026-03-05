#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PORT="${PORT:-5000}"
WORKERS="${WORKERS:-2}"
PID_FILE="${PID_FILE:-backend.pid}"
LOG_FILE="${LOG_FILE:-backend.log}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 not found."
  exit 1
fi

python3 -m pip install -r requirements.txt

if [[ -f "${PID_FILE}" ]] && kill -0 "$(cat "${PID_FILE}")" >/dev/null 2>&1; then
  echo "Backend is already running. PID: $(cat "${PID_FILE}")"
  exit 0
fi

echo "Starting backend in background on 0.0.0.0:${PORT} with ${WORKERS} workers..."
gunicorn \
  -w "${WORKERS}" \
  -b "0.0.0.0:${PORT}" \
  --daemon \
  --pid "${PID_FILE}" \
  --access-logfile "${LOG_FILE}" \
  --error-logfile "${LOG_FILE}" \
  app:app

echo "Started. PID: $(cat "${PID_FILE}")"
echo "Log file: ${SCRIPT_DIR}/${LOG_FILE}"
