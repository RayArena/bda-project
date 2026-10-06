@echo off
setlocal
cd /d "%~dp0\.."

REM Activate virtual environment if available
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

echo Starting PySpark Kafka Consumer and Sentiment Classifier...
python Kafka-PySpark\consumer-pyspark.py
pause
