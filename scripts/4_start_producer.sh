#!/usr/bin/env bash
# 4 - Kafka tweet producer (macOS / Linux)
set -euo pipefail
source "$(dirname "$0")/load_env.sh"

cd "$PROJECT_ROOT"
export PYTHONIOENCODING=utf-8

echo "=========================================================="
echo "Starting Kafka tweet producer (topic: ${KAFKA_TOPIC:-numtest})..."
echo "Python: $PYTHON_EXE"
echo "=========================================================="
exec "$PYTHON_EXE" "Kafka-PySpark/producer-validation-tweets.py"
