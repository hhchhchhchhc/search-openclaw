#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${VENV_DIR:-$ROOT/.venv}"

if [ ! -x "$VENV_DIR/bin/search-openclaw" ]; then
  echo "error: Search OpenClaw is not installed yet."
  echo "run: ./scripts/install.sh"
  exit 1
fi

exec "$VENV_DIR/bin/search-openclaw" "$@"
