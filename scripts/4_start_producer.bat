@echo off
title 4 - Kafka Tweet Producer
setlocal
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0\.."

REM Use virtual environment python if available
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else if exist "venv\Scripts\python.exe" (
    set "PYTHON_EXE=venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

echo ==========================================================
echo Starting Kafka Tweet Producer (streaming to topic 'numtest')...
echo Python: %PYTHON_EXE%
echo ==========================================================
%PYTHON_EXE% Kafka-PySpark\producer-validation-tweets.py
pause
