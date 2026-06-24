#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend"
REQUIREMENTS_FILE="$ROOT_DIR/requirements.txt"

BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"
API_URL="${NEXT_PUBLIC_API_URL:-http://localhost:${BACKEND_PORT}}"

backend_pid=""
frontend_pid=""

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

ensure_backend_deps() {
  if python -c "import fastapi, uvicorn, openai, dotenv, sqlalchemy" >/dev/null 2>&1; then
    return
  fi

  echo "Installing backend dependencies from requirements.txt"
  (
    cd "$ROOT_DIR"
    python -m pip install -r "$REQUIREMENTS_FILE"
  )
}

ensure_frontend_deps() {
  if [[ -x "$FRONTEND_DIR/node_modules/.bin/next" ]]; then
    return
  fi

  echo "Installing frontend dependencies"
  (
    cd "$FRONTEND_DIR"
    npm install
  )
}

cleanup() {
  if [[ -n "${frontend_pid}" ]] && kill -0 "${frontend_pid}" 2>/dev/null; then
    kill "${frontend_pid}" 2>/dev/null || true
  fi
  if [[ -n "${backend_pid}" ]] && kill -0 "${backend_pid}" 2>/dev/null; then
    kill "${backend_pid}" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

require_cmd python
require_cmd npm
ensure_backend_deps
ensure_frontend_deps

echo "Starting backend on http://localhost:${BACKEND_PORT}"
(
  cd "$ROOT_DIR"
  python backend/main.py
) &
backend_pid=$!

echo "Starting frontend on http://localhost:${FRONTEND_PORT}"
(
  cd "$FRONTEND_DIR"
  NEXT_PUBLIC_API_URL="$API_URL" npm run dev -- --port "${FRONTEND_PORT}"
) &
frontend_pid=$!

echo
echo "Backend:  http://localhost:${BACKEND_PORT}"
echo "Frontend: http://localhost:${FRONTEND_PORT}"
echo "API URL:  ${API_URL}"
echo "Press Ctrl+C to stop both."
echo

wait "${backend_pid}" "${frontend_pid}"
