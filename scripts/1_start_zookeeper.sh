#!/usr/bin/env bash
# 1 - Start Apache ZooKeeper (macOS / Linux)
set -euo pipefail
source "$(dirname "$0")/load_env.sh"

: "${KAFKA_HOME:?KAFKA_HOME is not set in .env}"
if [ ! -x "$KAFKA_HOME/bin/zookeeper-server-start.sh" ]; then
    echo "[error] zookeeper-server-start.sh not found under KAFKA_HOME=$KAFKA_HOME"
    echo "        Fix KAFKA_HOME in your .env to point at your Kafka folder."
    exit 1
fi

echo "=========================================================="
echo "Starting Apache ZooKeeper on port 2181..."
echo "Using Kafka from: $KAFKA_HOME"
echo "=========================================================="
exec "$KAFKA_HOME/bin/zookeeper-server-start.sh" "$KAFKA_HOME/config/zookeeper.properties"
