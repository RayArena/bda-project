# Big Data Project: Real-Time Twitter Sentiment Analysis

Real-time Twitter sentiment analysis and classification using **Apache Kafka**, **Apache Spark (PySpark MLLib & Streaming)**, **MongoDB**, and a **Django Dashboard** — running completely **natively without Docker**.

---

## 🏛️ Project Architecture

```
[ Twitter Dataset / Producer ]
              │
              ▼
       [ Apache Kafka ]
         (Topic: numtest)
              │
              ▼
   [ PySpark Streaming Consumer ]
   (Logistic Regression NLP Model)
              │
              ▼
        [ MongoDB Database ]
        (Database: bigdata_project, Collection: tweets)
              │
              ▼
       [ Django Dashboard ]
    (Real-time charts, analytics, and custom tweet classifier)
```

- **Apache Kafka**: Ingests streaming tweet records.
- **Spark Streaming (PySpark)**: Reads streaming tweets from Kafka, runs the ML sentiment classifier, and writes results to MongoDB.
- **MongoDB**: Persists classified tweets and sentiment statistics.
- **Django Dashboard**: Visualizes sentiment distribution, top word frequencies, and allows on-demand tweet classification.

---

## 📁 Repository Structure

```
Real-Time-Twitter-Sentiment-Analysis/
├── Django-Dashboard/            # Django web application
│   ├── BigDataProject/          # Django project settings & static files
│   ├── dashboard/               # Dashboard app views, templates & URLs
│   ├── logistic_regression_model.pkl # Model copy for on-demand classification
│   └── manage.py                # Django CLI management script
├── Kafka-PySpark/               # Streaming pipelines
│   ├── consumer-pyspark.py      # PySpark Kafka consumer & sentiment analyzer
│   ├── producer-validation-tweets.py # Kafka tweet producer
│   ├── logistic_regression_model.pkl # PySpark trained PipelineModel
│   └── twitter_validation.csv   # Validation dataset used for streaming
├── ML PySpark Model/            # Training datasets & model training notebook
├── scripts/                     # Convenient native Windows launch scripts
│   ├── start_local_kafka.bat    # Helper to start Kafka/ZooKeeper
│   ├── run_producer.bat         # Start Kafka tweet producer
│   ├── run_consumer.bat         # Start PySpark consumer
│   └── run_dashboard.bat        # Start Django web server
├── tools/                       # Utilities (e.g. tweet export normalizer)
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

---

## ⚙️ Prerequisites (Local Native Setup)

Ensure you have the following installed on your machine:

1. **Python 3.10+**
   - Verify: `python --version`
2. **Java JDK (JDK 8, 11, 17, or 21+)**
   - Required by Apache Spark and Kafka.
   - Verify: `java -version`
   - Set `JAVA_HOME` environment variable (e.g. `C:\Program Files\Java\jdk-23`).
3. **MongoDB Community Server** (or a free MongoDB Atlas cluster)
   - Download from: [https://www.mongodb.com/try/download/community](https://www.mongodb.com/try/download/community)
   - MongoDB Compass (recommended for viewing data): [https://www.mongodb.com/products/tools/compass](https://www.mongodb.com/products/tools/compass)
4. **Apache Kafka Binary**
   - Download the Scala binary release (e.g. `kafka_2.13-3.x.x.tgz`) from [https://kafka.apache.org/downloads](https://kafka.apache.org/downloads).
   - Extract it to a short path without spaces, such as `C:\kafka`.

---

## 🚀 Setup & Execution Guide (Step-by-Step)

### Step 1: Clone Repository & Set Up Python Environment

Open PowerShell or Command Prompt in the project folder:

```powershell
# 1. Create a Python virtual environment
python -m venv venv

# 2. Activate the virtual environment
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Or Windows Command Prompt (CMD):
venv\Scripts\activate.bat

# 3. Install required dependencies
pip install -r requirements.txt
```

---

### Step 2: Environment Configuration (.env)

The project includes a `.env` configuration file in the project root:
- **`MONGO_URI`**: Set to your local MongoDB instance (e.g., `mongodb://localhost:27017/`) or MongoDB Atlas cloud connection URI (`mongodb+srv://...`).
- **`MONGO_DB_NAME`**: MongoDB database name (default: `bigdata_project`).
- **`MONGO_COLLECTION`**: MongoDB collection name (default: `tweets`).
- **`KAFKA_BOOTSTRAP_SERVERS`**: Kafka broker address (default: `localhost:9092`).
- **`KAFKA_TOPIC`**: Topic name (default: `numtest`).

---

### Step 3: Start MongoDB

Make sure MongoDB is running on `localhost:27017`:

- **Windows Service**: Open `services.msc` and ensure **MongoDB Server** is running, or execute in an Administrator terminal:
  ```powershell
  net start MongoDB
  ```
- **Manual Start**: If running from a standalone binary:
  ```powershell
  mongod --dbpath "C:\data\db"
  ```

---

### Step 3: Start Apache Kafka (Natively on Windows)

Open a new terminal window for ZooKeeper and another for Kafka Broker (assuming Kafka is extracted at `C:\kafka`):

#### 3.1 Start ZooKeeper:
```cmd
C:\kafka\bin\windows\zookeeper-server-start.bat C:\kafka\config\zookeeper.properties
```

#### 3.2 Start Kafka Broker:
In a **new terminal**:
```cmd
C:\kafka\bin\windows\kafka-server-start.bat C:\kafka\config\server.properties
```

*(Optional) Create the topic `numtest` (Kafka auto-creates topics by default, but you can create it explicitly):*
```cmd
C:\kafka\bin\windows\kafka-topics.bat --create --topic numtest --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

> **Tip:** You can also run `scripts\start_local_kafka.bat` from this repository for an interactive menu.

---

### Step 4: Run the PySpark Consumer

In a **new terminal** (with your Python virtual environment activated):

```powershell
python Kafka-PySpark\consumer-pyspark.py
```
*(Or double-click `scripts\run_consumer.bat`)*

This script:
1. Connects to Kafka topic `numtest`.
2. Connects to MongoDB `bigdata_project` database.
3. Loads the trained ML sentiment model.
4. Waits to consume and classify incoming tweets.

---

### Step 5: Run the Kafka Tweet Producer

In a **new terminal** (with your Python virtual environment activated):

```powershell
python Kafka-PySpark\producer-validation-tweets.py
```
*(Or double-click `scripts\run_producer.bat`)*

This script reads tweets from `Kafka-PySpark/twitter_validation.csv` and streams them into Kafka every 2 seconds. You will see the consumer classify the sentiments in real-time and store them in MongoDB!

---

### Step 6: Start the Django Web Dashboard

In a **new terminal** (with your Python virtual environment activated):

```powershell
cd Django-Dashboard

# Apply initial migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start the web server
python manage.py runserver
```
*(Or double-click `scripts\run_dashboard.bat`)*

---

### Step 7: Open the Dashboard

Open your web browser and navigate to:

👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

- **Dashboard**: Displays total tweets processed, sentiment percentage breakdown (Positive, Negative, Neutral, Irrelevant), and top word frequency charts.
- **Custom Classifier**: Visit **[http://127.0.0.1:8000/classify](http://127.0.0.1:8000/classify)** to enter any custom tweet text and get an instant sentiment prediction!

---

## 🛠️ Helpful Utilities

### Converting Custom Tweet Exports
To stream custom tweets from Twitter/X or TweetClaw into the pipeline:
```powershell
python tools\normalize_tweet_export.py examples\tweetclaw-reviewed-export.csv --output Kafka-PySpark\twitter_validation.csv
```

---

## 💡 Troubleshooting & Notes

1. **Windows Java Error / PySpark**:
   - Ensure `JAVA_HOME` points to your JDK directory without a trailing slash (e.g., `set JAVA_HOME=C:\Program Files\Java\jdk-23`).
2. **Kafka Path Length on Windows**:
   - Keep your Kafka folder near the drive root (e.g., `C:\kafka`) to avoid Windows `The input line is too long` errors in batch files.
3. **MongoDB Connection**:
   - PySpark and Django default to `mongodb://localhost:27017/`. Ensure MongoDB is listening on port 27017 before starting the consumer.
