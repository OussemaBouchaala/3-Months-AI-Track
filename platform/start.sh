#!/usr/bin/env bash
# Starts Bench with the .venv next to platform/ (run setup once), else python3.
cd "$(dirname "$0")"
PY=../.venv/bin/python
[ -x "$PY" ] || PY=python3
exec "$PY" server.py
