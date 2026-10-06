@echo off
setlocal
cd /d "%~dp0\..\Django-Dashboard"

REM Activate virtual environment if available
if exist "..\venv\Scripts\activate.bat" (
    call ..\venv\Scripts\activate.bat
) else if exist "..\.venv\Scripts\activate.bat" (
    call ..\.venv\Scripts\activate.bat
)

echo Starting Django Sentiment Analysis Dashboard on http://127.0.0.1:8000 ...
python manage.py runserver 127.0.0.1:8000
pause
