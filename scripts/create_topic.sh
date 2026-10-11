#!/usr/bin/env bash
# Create the Kafka topic used by the pipeline (macOS / Linux)
set -euo pipefail
source "$(dirname "$0")/load_env.sh"

: "${KAFKA_HOME:?KAFKA_HOME is not set in .env}"
TOPIC="${KAFKA_TOPIC:-numtest}"
BOOTSTRAP="${KAFKA_BOOTSTRAP_SERVERS:-localhost:9092}"

echo "Creating topic '$TOPIC' on $BOOTSTRAP ..."
exec "$KAFKA_HOME/bin/kafka-topics.sh" --create --if-not-exists \
    --topic "$TOPIC" \
    --bootstrap-server "$BOOTSTRAP" \
    --partitions 1 --replication-factor 1
