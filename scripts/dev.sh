#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PYTHON="$ROOT_DIR/.venv/bin/python"

if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "Missing virtual environment at $ROOT_DIR/.venv. Run \`make install\` first." >&2
  exit 1
fi

cd "$ROOT_DIR"

export PYTHONPATH="$ROOT_DIR/src${PYTHONPATH:+:$PYTHONPATH}"

HOST="${DOCX_VALIDATE_HOST:-127.0.0.1}"
PORT="${DOCX_VALIDATE_PORT:-8000}"

exec "$VENV_PYTHON" -m uvicorn docx_validate.main:app --host "$HOST" --port "$PORT" --reload
