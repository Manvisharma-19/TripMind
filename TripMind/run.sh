#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/backend"
if [ ! -d venv ]; then python3.12 -m venv venv 2>/dev/null || python3 -m venv venv; fi
source venv/bin/activate
pip install -q -r requirements.txt
echo "Starting TripMind at http://localhost:8000"
uvicorn main:app --reload
