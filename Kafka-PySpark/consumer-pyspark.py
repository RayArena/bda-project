import os
import sys
import re
import platform
from pathlib import Path
# Reconfigure standard output to handle emojis safely on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env as early as possible so every path
# below (JAVA_HOME, HADOOP_HOME, MODEL_PATH, ...) can be overridden there.
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT_DIR / ".env")
except ImportError:
    pass

# Ensure PYSPARK_PYTHON points at the running interpreter
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

# JAVA_HOME: honor .env override if provided
java_home = os.getenv("JAVA_HOME")
if java_home:
    os.environ["JAVA_HOME"] = java_home

# HADOOP_HOME: only needed on Windows (winutils). Use .env value if set,
# otherwise auto-detect the bundled ./hadoop folder on Windows only.
hadoop_home = os.getenv("HADOOP_HOME")
if not hadoop_home and platform.system() == "Windows":
    bundled = ROOT_DIR / "hadoop"
    if bundled.exists():
        hadoop_home = str(bundled)
if hadoop_home:
    os.environ["HADOOP_HOME"] = hadoop_home
    os.environ["PATH"] = str(Path(hadoop_home) / "bin") + os.pathsep + os.environ.get("PATH", "")

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

# Resolve model path: MODEL_PATH from .env wins, else the in-repo default.
SCRIPT_DIR = Path(__file__).resolve().parent
model_env = os.getenv("MODEL_PATH")
if model_env:
    model_path = Path(model_env)
else:
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
    # Select by column name (robust to pipeline column ordering changes)
    row = processed_validation.select("prediction", "probability").collect()[0]
    prediction = row["prediction"]
    probability = row["probability"]
    sentiment_label = class_index_mapping.get(int(prediction), "Neutral")

    # Model confidence for this prediction = highest class probability.
    # This is the per-tweet "accuracy"/certainty the model assigns.
    confidence = round(float(max(probability)) * 100, 2)
    # Full per-class probability distribution (handy for the dashboard / audits)
    class_probabilities = {
        class_index_mapping.get(i, str(i)): round(float(p) * 100, 2)
        for i, p in enumerate(probability)
    }

    if collection is not None:
        try:
            tweet_doc = {
                "tweet": tweet,
                "prediction": sentiment_label,
                "confidence": confidence,
                "class_probabilities": class_probabilities,
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
        print(f"-> Confidence       : {confidence}%")
        print("=" * 60)
    except Exception:
        safe_tweet = tweet.encode('ascii', errors='replace').decode('ascii')
        print(f"-> Original Tweet   : {safe_tweet}")
        print(f"-> Predicted Label  : {sentiment_label} ({prediction}) @ {confidence}%")
