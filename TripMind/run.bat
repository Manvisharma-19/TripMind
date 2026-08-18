@echo off
REM Windows one-click start. IMPORTANT: needs Python 3.12 (not 3.14).
cd /d "%~dp0backend"
if not exist venv ( echo Creating venv... & py -3.12 -m venv venv )
call venv\Scripts\activate
pip install -q -r requirements.txt
echo Starting TripMind at http://localhost:8000
uvicorn main:app --reload
pause
