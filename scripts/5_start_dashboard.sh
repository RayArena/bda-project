#!/usr/bin/env bash
# 5 - Django dashboard (macOS / Linux)
set -euo pipefail
source "$(dirname "$0")/load_env.sh"

cd "$PROJECT_ROOT/Django-Dashboard"

echo "=========================================================="
echo "Starting Django dashboard on http://${DJANGO_HOST}:${DJANGO_PORT} ..."
echo "Python: $PYTHON_EXE"
echo "=========================================================="
exec "$PYTHON_EXE" manage.py runserver "${DJANGO_HOST}:${DJANGO_PORT}"
