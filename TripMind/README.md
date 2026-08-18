# TripMind ✈️ — AI Trip Planner (modular backend)

Describe a trip in plain English — *"somewhere warm in December, under ₹30,000,
5 days, from Delhi"* — and TripMind picks a destination, a flight and a hotel
within budget, builds a day-by-day itinerary, and saves it to **My Trips**.

This is your original modular `app/` architecture, **completed and fixed** so it
runs with one command and no errors.

---

## ✨ What's new in this version (feature upgrades)

- **27 destinations** (was 9), from a single shared catalog (`app/catalog.py`) —
  Goa, Kerala, Jaipur, Udaipur, Jaisalmer, Agra, **Ahmedabad**, Varanasi,
  Rishikesh, Manali, Shimla, Leh, Darjeeling, Shillong, Coorg, Mysore, Amritsar,
  Andaman, Pondicherry, plus Bangkok, Bali, Dubai, Singapore, Maldives, Kathmandu.
  Your existing database upgrades to the full list automatically on next start.
- **Understands real place names + typos.** "a trip to ahemdabad" now correctly
  plans **Ahmedabad** (fuzzy matching), and if you name a place it genuinely
  doesn't cover, it says so honestly instead of returning a random city.
- **Rich chat cards.** Each plan now renders as a polished boarding-pass card in
  the chat — route, flight, hotel, highlighted total, day-by-day, alternatives,
  and inline **Download PDF** + **Show map** buttons.
- **Animated landing page** (`landing.html`): CSS/SVG beach, mountains and
  monument scenes, a plane crossing the sky, destination postcards and a
  how-it-works section. Logged-out visitors land here first.
- **Multi-turn edits**: "make it cheaper", "try mountains instead", "make it
  longer", "somewhere else" refine the previous trip.
- **PDF itinerary export** (server-side `fpdf2`) and **map view** (OpenStreetMap,
  no API key) on every trip.
- **Settings page** (`settings.html`): save a home city (default departure) and
  budget style, which the planner respects.
---

## 1. Why your version wouldn't run (and what I changed)

| Problem | Fix |
|---|---|
| **Missing files.** `main.py`/`auth.py` import `app.models.db_models`, and `main.py` imports `app.routes.auth_routes / chat_routes / booking_routes` — none of those files existed, so Python failed at import (`ModuleNotFoundError`). | Wrote those missing modules to match your imports exactly. |
| **Python 3.14** (your venv was built with `Python314`). Many packages have no wheels for 3.14 yet, so `pip` tries to compile them and fails — the wall of red errors. | Use **Python 3.12**. Also removed the packages that don't build easily. |
| **Empty database** (0 flights/hotels/docs) so planning returned nothing. | The app now **auto-seeds** on startup using your `seed_data.py`. |
| `langchain`, `langgraph`, `langchain-openai`, `passlib` in requirements — heavy/fragile and unused by the working app. | Removed. Your `auth.py` uses `bcrypt` + `python-jose` directly; those stay. |
| `api.js` hard-coded `http://localhost:8000` (breaks when deployed) and frontend/backend were different origins (CORS). | `api.js` now uses `window.location.origin`, and the backend **serves the frontend**, so it's one origin. |

Your files kept as-is: **`database.py`, `auth.py`, `seed_data.py`** (I only
widened the seed's date range so months like December appear).

---

## 2. Folder layout

Unzip and you get exactly this. Keep it — the imports depend on it.

```
TripMind/
├─ backend/
│  ├─ main.py                  ← app entry point (uvicorn main:app)
│  ├─ requirements.txt
│  ├─ .env.example             ← copy to .env (optional)
│  └─ app/
│     ├─ __init__.py
│     ├─ database.py           ← YOUR file
│     ├─ auth.py               ← YOUR file (bcrypt + JWT)
│     ├─ seed_data.py          ← YOUR file (data)
│     ├─ schemas.py            ← request/response shapes
│     ├─ planner.py            ← the trip-planning "AI"
│     ├─ models/
│     │  └─ db_models.py       ← the database tables (was missing)
│     └─ routes/
│        ├─ auth_routes.py     ← /auth/register, /auth/login, /auth/me
│        ├─ chat_routes.py     ← /chat
│        └─ booking_routes.py  ← /bookings, /stats, cancel, preferences
└─ frontend/                   ← the website (served by the backend)
   ├─ index.html  login.html  register.html  chat.html  trips.html
   ├─ api.js  style.css
```

---

## 3. Run it locally (⚠️ use Python 3.12)

**First, install Python 3.12** from python.org if you don't have it. Check:
```
py -3.12 --version        # Windows
python3.12 --version      # Mac/Linux
```

Then, from the `backend` folder:

**Windows (PowerShell / CMD)**
```bat
cd backend
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**Mac / Linux**
```bash
cd backend
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open **http://localhost:8000**. Register, plan a trip, check My Trips.
(Or just run `run.bat` on Windows / `./run.sh` on Mac-Linux from the project
root — they do all of the above.)

Interactive API docs: **http://localhost:8000/docs**.

> Already made a `venv` with Python 3.14? Delete that `venv` folder first, then
> recreate it with 3.12 as above. Mixing versions is what causes the errors.

---

## 4. The API

| Method & path | Purpose |
|---|---|
| `POST /auth/register` | Create account → token |
| `POST /auth/login` | Log in → token |
| `GET /auth/me` | Current user |
| `POST /chat` | Plan a trip; auto-saves a booking |
| `GET /bookings` | List my trips |
| `POST /bookings/{id}/cancel` | Cancel a trip |
| `GET /stats` | Dashboard numbers |
| `PUT /preferences` | Save home city / budget style |
| `GET /health` | Liveness check |

All except register/login/health need `Authorization: Bearer <token>` (the
frontend adds this automatically).

---

## 5. How the planner works (the "AI" part)

`app/planner.py` does five things with each message:
1. **Parse** budget (`₹30,000`, `30k`), nights (`5 days` → 4 nights), month
   (`December`, `winter`), origin (`from Delhi`), and any named place (`Bali`).
2. **Score** each destination by how well its *vibes* (beach, mountains,
   heritage…) and *best season* match the request.
3. **Build an option**: cheapest flight from your city + the best-rated hotel
   whose stay fits the leftover budget.
4. **Rank**: within budget first, then best match, then cheapest.
5. **Write** a friendly plan with a day-by-day itinerary and alternatives, and
   **save** it to your trips.

It's deterministic, so it always works. The optional LLM (below) only *rewords*
the reply; the facts and choices are decided in Python. If the LLM call fails,
the built-in text is used, so your demo can't break because of it.

---

## 6. Optional: turn on the LLM (Groq)

Not required. To enable it, copy `.env.example` to `.env` and set:
```
OPENAI_API_KEY=gsk_your_groq_key_here
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.1-8b-instant
```
Your uploaded key started with `gsk_`, which is a **Groq** key — the settings
above match it. ⚠️ Regenerate that key in the Groq console; it was shared in
plain text and should be considered compromised. Never commit `.env` to GitHub
(the `.gitignore` already excludes it).

---

## 7. Deploy (one service, free tier)

Because the backend serves the frontend, you deploy just the backend.

**Render.com**
1. Push to a GitHub repo.
2. New → Web Service → connect the repo.
3. Root Directory: `backend` · Runtime: Python **3.12**
   (add a file `backend/runtime.txt` containing `python-3.12.7` to pin it)
4. Build: `pip install -r requirements.txt`
5. Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Deploy and open the URL — the site loads automatically.

SQLite resets on restart on free hosts (fine for a demo). For permanent data,
create a free Postgres DB and set `DATABASE_URL` to its URL — the code already
supports it.

---

## 8. Troubleshooting

| Symptom | Fix |
|---|---|
| Long pip errors about building wheels / "Rust"/"C compiler" | You're on Python 3.14. Recreate the venv with **3.12**. |
| `ModuleNotFoundError: No module named 'app'` | Run `uvicorn main:app` **from inside the `backend` folder**, not elsewhere. |
| `Email already registered` | Log in instead, or use a new email. |
| My Trips is empty | Plan a trip first; each successful plan is saved. |
| Port 8000 busy | `uvicorn main:app --reload --port 8080`, open `:8080`. |

---

## 9. Nice extensions for your viva
Multi-turn tweaks ("make it cheaper", "try mountains"), real flight data via an
API, PDF/email itinerary export, a map view, and using saved `home_city` to
pre-fill the origin.
