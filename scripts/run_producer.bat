@echo off
setlocal
cd /d "%~dp0\.."

REM Activate virtual environment if available
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

echo Starting Kafka Tweet Producer...
python Kafka-PySpark\producer-validation-tweets.py
pause
