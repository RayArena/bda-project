@echo off
title 3 - PySpark Sentiment Consumer
setlocal
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0\.."

if "%JAVA_HOME%"=="" (
    if exist "C:\Program Files\Java\jdk-23" set "JAVA_HOME=C:\Program Files\Java\jdk-23"
)

REM Set HADOOP_HOME for Windows PySpark model loading
set "HADOOP_HOME=%~dp0..\hadoop"
set "PATH=%HADOOP_HOME%\bin;%PATH%"

REM Use virtual environment python if available
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else if exist "venv\Scripts\python.exe" (
    set "PYTHON_EXE=venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

REM Ensure Spark workers use the exact python environment
set "PYSPARK_PYTHON=%PYTHON_EXE%"
set "PYSPARK_DRIVER_PYTHON=%PYTHON_EXE%"

echo ==========================================================
echo Starting PySpark Kafka Consumer and Sentiment Classifier...
echo Python: %PYTHON_EXE%
echo ==========================================================
%PYTHON_EXE% Kafka-PySpark\consumer-pyspark.py
pause
