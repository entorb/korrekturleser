#!/bin/sh
set -e
SCRIPT_DIR="$(dirname "$0")"
cd "$SCRIPT_DIR/.."

FASTAPI_PID=""

cleanup() {
  [ -n "$FASTAPI_PID" ] && kill "$FASTAPI_PID" 2>/dev/null || true
}
trap cleanup EXIT

# start FastAPI if not already running
if ! curl -sf localhost:9002/openapi.json >/dev/null 2>&1; then
  uv run --no-build uvicorn fastapi_app.main:app --host localhost --port 9002 &
  FASTAPI_PID=$!
  i=0
  until curl -sf localhost:9002/openapi.json >/dev/null 2>&1; do
    i=$((i + 1))
    [ "$i" -ge 20 ] && {
      echo "ERROR: uvicorn failed to start" >&2
      exit 1
    }
    sleep 0.5
  done
fi

rm -f openapi-ts-error-*.log
pnpm exec openapi-ts && uv run --no-build python scripts/gen_mode_descriptions.py
