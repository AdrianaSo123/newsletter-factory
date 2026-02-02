#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -x .venv/bin/python ]; then
  echo "ERROR: .venv not found. Run scripts/setup_venv.sh first." >&2
  exit 1
fi

VENV_PY="$(pwd)/.venv/bin/python"
"$VENV_PY" -m pytest
