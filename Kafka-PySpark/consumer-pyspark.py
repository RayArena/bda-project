import os
import sys
import re
from pathlib import Path
# Reconfigure standard output to handle emojis safely on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
# Ensure PYSPARK_PYTHON and HADOOP_HOME are set on Windows
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
ROOT_DIR = Path(__file__).resolve().parent.parent
hadoop_dir = ROOT_DIR / "hadoop"
if hadoop_dir.exists():
    os.environ["HADOOP_HOME"] = str(hadoop_dir)
    os.environ["PATH"] = str(hadoop_dir / "bin") + os.pathsep + os.environ.get("PATH", "")

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

from json import loads
import nltk
from pymongo import MongoClient
from kafka import KafkaConsumer
from pyspark.ml import PipelineModel
from pyspark.sql import SparkSession

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT_DIR / ".env")
except ImportError:
    pass

# Connect to MongoDB (configurable via .env / environment variables)
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
mongo_db_name = os.getenv("MONGO_DB_NAME", "bigdata_project")
mongo_collection = os.getenv("MONGO_COLLECTION", "tweets")
try:
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
    client.server_info()
    db = client[mongo_db_name]
    collection = db[mongo_collection]
    print(f"Connected successfully to MongoDB ({mongo_uri}), db='{mongo_db_name}', collection='{mongo_collection}'.")
except Exception as err:
    print(f"[Warning] Could not connect to MongoDB at {mongo_uri}.")
    print("Ensure MongoDB service is running or check your MONGO_URI. Continuing without Mongo persistence...")
    collection = None

# Download stopwords and tokenizers
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

# SparkSession
print("Initializing SparkSession...")
spark = SparkSession.builder \
    .appName("classify tweets") \
    .config("spark.ui.showConsoleProgress", "false") \
    .getOrCreate()
spark.sparkContext.setLogLevel("WARN")

# Load model resolving path dynamically
SCRIPT_DIR = Path(__file__).resolve().parent
model_path = SCRIPT_DIR / "logistic_regression_model.pkl"
if not model_path.exists():
    model_path = Path("logistic_regression_model.pkl")

print(f"Loading sentiment model from: {model_path}...")
pipeline = PipelineModel.load(str(model_path))
print("Model loaded successfully.")

def clean_text(text):
    if text is not None:
        text = re.sub(r'https?://\S+|www\.\S+|\.com\S+|youtu\.be/\S+', '', text)
        text = re.sub(r'(@|#)\w+', '', text)
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    return ''

class_index_mapping = {0: "Negative", 1: "Positive", 2: "Neutral", 3: "Irrelevant"}

topic_name = os.getenv('KAFKA_TOPIC', 'numtest')
kafka_bootstrap = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
kafka_servers = [s.strip() for s in kafka_bootstrap.split(',') if s.strip()]
consumer_group = os.getenv('KAFKA_CONSUMER_GROUP', 'my-group')
print(f"Connecting to Kafka topic '{topic_name}' on {kafka_bootstrap} (group: '{consumer_group}')...")
try:
    consumer = KafkaConsumer(
        topic_name,
        bootstrap_servers=kafka_servers,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id=consumer_group,
        value_deserializer=lambda x: loads(x.decode('utf-8'))
    )
    print("Consumer connected. Waiting for streaming tweets...")
except Exception as e:
    print(f"[Error] Failed to connect to Kafka Broker: {e}")
    raise SystemExit(1)

for message in consumer:
    val = message.value
    if isinstance(val, list) and len(val) > 0:
        tweet = val[-1]
    else:
        tweet = str(val)

    preprocessed_tweet = clean_text(tweet)
    data = [(preprocessed_tweet,)]
    df = spark.createDataFrame(data, ["Text"])
    processed_validation = pipeline.transform(df)
    prediction = processed_validation.collect()[0][6]
    sentiment_label = class_index_mapping.get(int(prediction), "Neutral")

    if collection is not None:
        try:
            tweet_doc = {
                "tweet": tweet,
                "prediction": sentiment_label
            }
            collection.insert_one(tweet_doc)
            print("[MongoDB] Persisted to database.")
        except Exception as e:
            print(f"[MongoDB Error] {e}")

    try:
        print("=" * 60)
        print(f"-> Original Tweet   : {tweet}")
        print(f"-> Preprocessed     : {preprocessed_tweet}")
        print(f"-> Predicted Label  : {sentiment_label} ({prediction})")
        print("=" * 60)
    except Exception:
        safe_tweet = tweet.encode('ascii', errors='replace').decode('ascii')
        print(f"-> Original Tweet   : {safe_tweet}")
        print(f"-> Predicted Label  : {sentiment_label} ({prediction})")
