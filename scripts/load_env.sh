#!/usr/bin/env bash
# =====================================================================
# Shared environment loader for all pipeline scripts (macOS / Linux).
# Sourced by the other *.sh scripts. Resolves the project root, loads
# every value from the project .env, and fills in sensible defaults.
#
# Because everything reads from .env, changing a path there (JAVA_HOME,
# KAFKA_HOME, MODEL_PATH, VALIDATION_CSV, ...) applies to every script.
# =====================================================================

# Directory of THIS file, then the project root (its parent).
_LOADER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PROJECT_ROOT="$(cd "$_LOADER_DIR/.." && pwd)"

# Load .env (export every KEY=VALUE line; comments/blank lines are fine).
ENV_FILE="$PROJECT_ROOT/.env"
if [ -f "$ENV_FILE" ]; then
    set -a
    # shellcheck disable=SC1090
    . "$ENV_FILE"
    set +a
else
    echo "[warn] .env not found at $ENV_FILE — using built-in defaults."
fi

# Python interpreter: .env override, else project venv, else python3.
if [ -z "${PYTHON_EXE:-}" ]; then
    if [ -x "$PROJECT_ROOT/.venv/bin/python" ]; then
        PYTHON_EXE="$PROJECT_ROOT/.venv/bin/python"
    elif [ -x "$PROJECT_ROOT/venv/bin/python" ]; then
        PYTHON_EXE="$PROJECT_ROOT/venv/bin/python"
    else
        PYTHON_EXE="python3"
    fi
fi
export PYTHON_EXE

# Export JAVA_HOME / PATH for Kafka + Spark if provided in .env.
if [ -n "${JAVA_HOME:-}" ]; then
    export JAVA_HOME
    export PATH="$JAVA_HOME/bin:$PATH"
fi

# Spark workers must use the same interpreter.
export PYSPARK_PYTHON="$PYTHON_EXE"
export PYSPARK_DRIVER_PYTHON="$PYTHON_EXE"

# Django host/port defaults.
export DJANGO_HOST="${DJANGO_HOST:-127.0.0.1}"
export DJANGO_PORT="${DJANGO_PORT:-8000}"
