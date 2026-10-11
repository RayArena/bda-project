from time import sleep
import csv
import json
import os
import sys
from pathlib import Path

# Reconfigure stdout for safe emoji printing on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
# Fix Python 3.12+ / 3.13 Windows 'ValueError: Invalid file descriptor: -1' in kafka client
import selectors
if hasattr(selectors, "SelectSelector"):
    _orig_unregister = selectors.SelectSelector.unregister
    def _safe_unregister(self, fileobj):
        try:
            return _orig_unregister(self, fileobj)
        except (ValueError, KeyError):
            for fd, key in list(self._fd_to_key.items()):
                if key.fileobj == fileobj:
                    self._fd_to_key.pop(fd, None)
                    self._readers.discard(fd)
                    self._writers.discard(fd)
                    return key
            return None
    selectors.SelectSelector.unregister = _safe_unregister

from kafka import KafkaProducer

# Resolve root dir and load .env if available
ROOT_DIR = Path(__file__).resolve().parent.parent
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT_DIR / ".env")
except ImportError:
    pass

# Resolve path to the tweets CSV: VALIDATION_CSV from .env wins, else in-repo default.
SCRIPT_DIR = Path(__file__).resolve().parent
csv_env = os.getenv('VALIDATION_CSV')
if csv_env:
    csv_path = Path(csv_env)
else:
    csv_path = SCRIPT_DIR / 'twitter_validation.csv'
    if not csv_path.exists():
        csv_path = Path('twitter_validation.csv')

topic_name = os.getenv('KAFKA_TOPIC', 'numtest')
kafka_bootstrap = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
kafka_servers = [s.strip() for s in kafka_bootstrap.split(',') if s.strip()]
print(f"Connecting to Kafka on {kafka_bootstrap} (topic: '{topic_name}')...")

try:
    producer = KafkaProducer(
        bootstrap_servers=kafka_servers,
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )
    print("Connected to Kafka producer successfully.")
except Exception as e:
    print(f"[Error] Could not connect to Kafka Broker on {kafka_bootstrap}: {e}")
    raise SystemExit(1)

print(f"Streaming data from {csv_path} to Kafka topic '{topic_name}'...")
with open(csv_path, mode='r', encoding='utf-8', errors='replace') as file_obj:
    reader_obj = csv.reader(file_obj)
    for data in reader_obj:
        if not data:
            continue
        tweet_preview = data[-1][:50] if len(data) > 3 else str(data)[:50]
        print(f"[Producer] Sent tweet: {tweet_preview}...")
        producer.send(topic_name, value=data)
        sleep(2)
