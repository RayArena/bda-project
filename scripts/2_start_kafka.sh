#!/usr/bin/env bash
# 2 - Start Apache Kafka broker (macOS / Linux)
set -euo pipefail
source "$(dirname "$0")/load_env.sh"

: "${KAFKA_HOME:?KAFKA_HOME is not set in .env}"
if [ ! -x "$KAFKA_HOME/bin/kafka-server-start.sh" ]; then
    echo "[error] kafka-server-start.sh not found under KAFKA_HOME=$KAFKA_HOME"
    echo "        Fix KAFKA_HOME in your .env to point at your Kafka folder."
    exit 1
fi

export KAFKA_HEAP_OPTS="${KAFKA_HEAP_OPTS:--Xmx1G -Xms1G}"

echo "=========================================================="
echo "Starting Apache Kafka broker on localhost:9092..."
echo "Using Kafka from: $KAFKA_HOME"
echo "=========================================================="
exec "$KAFKA_HOME/bin/kafka-server-start.sh" "$KAFKA_HOME/config/server.properties"
