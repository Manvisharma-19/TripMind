"""
app entry point — run with:  uvicorn main:app --reload   (from the backend/ folder)

Kept as close to your original main.py as possible. Two additions:
  1. On startup it seeds the reference data (flights/hotels/docs) if the tables
     are empty, so you don't have to remember to run the seed separately.
  2. It serves the frontend, so opening http://localhost:8000 shows the app and
     there are no cross-origin (CORS) problems during your demo.
"""

from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import engine
from app.models.db_models import Base
from app.routes import auth_routes, chat_routes, booking_routes
from app.seed_data import seed

# Create any missing tables.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TripMind API",
              description="Conversational AI trip planning agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(auth_routes.router)
app.include_router(chat_routes.router)
app.include_router(booking_routes.router)


@app.on_event("startup")
def _seed_on_startup():
    # seed() opens its own DB session and skips if data already exists.
    seed()


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "TripMind API"}


# Serve the frontend last, so the API routes above always take priority.
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")
