import os
import re
from pathlib import Path
import nltk

import sys

# Ensure PYSPARK_PYTHON and HADOOP_HOME are set on Windows
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
hadoop_dir = ROOT_DIR / "hadoop"
if hadoop_dir.exists():
    os.environ["HADOOP_HOME"] = str(hadoop_dir)
    os.environ["PATH"] = str(hadoop_dir / "bin") + os.pathsep + os.environ.get("PATH", "")

from pyspark.ml import PipelineModel
from pyspark.sql import SparkSession

nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

# Initialize SparkSession
spark = SparkSession.builder \
    .appName("classify tweets user") \
    .config("spark.ui.showConsoleProgress", "false") \
    .getOrCreate()
spark.sparkContext.setLogLevel("WARN")

# Resolve model path dynamically
BASE_DIR = Path(__file__).resolve().parent.parent
model_path = BASE_DIR / "logistic_regression_model.pkl"
if not model_path.exists():
    model_path = BASE_DIR.parent / "Kafka-PySpark" / "logistic_regression_model.pkl"

pipeline = PipelineModel.load(str(model_path))

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

def classify_text(text: str) -> dict:
    """Classify text and return the label plus the model's confidence.

    Returns a dict:
        {
          "label": <str>,                 # predicted sentiment
          "confidence": <float>,          # confidence (%) in the chosen class
          "probabilities": {label: pct},  # full per-class probability distribution
        }
    """
    preprocessed_tweet = clean_text(text)
    data = [(preprocessed_tweet,)]
    df = spark.createDataFrame(data, ["Text"])
    processed_validation = pipeline.transform(df)
    row = processed_validation.select("prediction", "probability").collect()[0]
    prediction = row["prediction"]
    probability = row["probability"]
    label = class_index_mapping.get(int(prediction), "Neutral")

    confidence = round(float(max(probability)) * 100, 2)
    probabilities = {
        class_index_mapping.get(i, str(i)): round(float(p) * 100, 2)
        for i, p in enumerate(probability)
    }

    print(f"[Classify User] Text: {text} -> Sentiment: {label} ({confidence}%)")
    return {"label": label, "confidence": confidence, "probabilities": probabilities}
