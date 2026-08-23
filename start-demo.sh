#!/usr/bin/env bash
# Start the public portfolio demo (Python mocks + static UI). No secrets required.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
export DEMO_MODE="${DEMO_MODE:-true}"
PY_DIR="$ROOT/python-service"
VENV="$PY_DIR/.venv-demo"
PY="$VENV/bin/python"

if [ ! -x "$PY" ]; then
  echo "Creating demo venv at python-service/.venv-demo"
  python3 -m venv "$VENV"
  "$VENV/bin/pip" install -U pip
  "$VENV/bin/pip" install -r "$PY_DIR/requirements.txt"
fi

cd "$PY_DIR"
echo "[demo] Python :8001  DEMO_MODE=$DEMO_MODE"
"$PY" -m uvicorn app:app --host 127.0.0.1 --port 8001 &
PY_PID=$!

cleanup() {
  kill "$PY_PID" 2>/dev/null || true
}
trap cleanup EXIT

sleep 2
if ! curl -sf "http://127.0.0.1:8001/health" >/dev/null; then
  echo "Python health check failed. See the uvicorn log above."
  wait "$PY_PID"
  exit 1
fi

echo "[demo] Frontend :8000  →  http://127.0.0.1:8000"
cd "$ROOT/web-demo"
python3 -m http.server 8000
