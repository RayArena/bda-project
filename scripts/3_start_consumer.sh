#!/usr/bin/env bash
# 3 - PySpark Kafka consumer + sentiment classifier (macOS / Linux)
set -euo pipefail
source "$(dirname "$0")/load_env.sh"

cd "$PROJECT_ROOT"
export PYTHONIOENCODING=utf-8

echo "=========================================================="
echo "Starting PySpark Kafka consumer and sentiment classifier..."
echo "Python: $PYTHON_EXE"
echo "=========================================================="
exec "$PYTHON_EXE" "Kafka-PySpark/consumer-pyspark.py"
