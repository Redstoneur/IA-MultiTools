#!/bin/sh
set -eu
cd -- "$(dirname -- "$0")"

if [ -n "${VIRTUAL_ENV:-}" ]; then
    PYTHON="$VIRTUAL_ENV/bin/python"
elif [ -x ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
else
    PYTHON=python3
fi

exec "$PYTHON" build.py "$@"
