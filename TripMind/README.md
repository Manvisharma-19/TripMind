# ✈️ TripMind — AI-Powered Trip Planner

> **Describe your perfect trip in natural language. TripMind turns it into a complete, budget-aware travel plan.**

TripMind is a full-stack **AI-powered travel planning application** that understands natural-language travel requests and automatically creates personalized trips based on **budget, duration, destination preferences, season, travel origin, and travel style**.

For example:

> **"Plan a warm 5-day trip from Delhi in December under ₹30,000."**

TripMind analyzes the request, recommends a suitable destination, selects a flight and hotel within the available budget, generates a day-by-day itinerary, and saves the trip to **My Trips**.

The application combines a **deterministic AI planning engine**, natural-language parsing, fuzzy destination matching, budget optimization, JWT authentication, PDF itinerary generation, and interactive maps into a single modular platform.

---

## 🌍 Why TripMind?

Planning a trip usually requires switching between multiple platforms for:

* Destination research
* Flight comparison
* Hotel selection
* Budget calculation
* Itinerary planning
* Saving travel plans

TripMind brings these steps together into one conversational experience.

Instead of filling out multiple forms, users can simply describe what they want:

```text
Somewhere peaceful with mountains, 5 days,
under ₹35,000 from Delhi.
```

TripMind converts that request into an actionable travel plan.

---

# ✨ Key Features

### 🧠 Natural-Language Trip Planning

Users can describe their requirements conversationally instead of using rigid forms.

TripMind understands information such as:

* Destination
* Budget
* Number of days/nights
* Travel month
* Departure city
* Travel preferences
* Destination vibes

Example:

```text
I want a 6-day mountain trip from Delhi
in December under ₹35,000.
```

---

### 🎯 Intelligent Destination Matching

TripMind maintains a centralized destination catalog containing destination metadata such as:

* Travel vibes
* Recommended seasons
* Coordinates
* Flight price estimates
* Hotel price estimates
* Destination descriptions

The planner scores destinations according to how closely they match the user's request.

Supported destinations include popular Indian and international locations such as:

**India**

Goa · Kochi · Munnar · Alleppey · Jaipur · Udaipur · Jaisalmer · Agra · Ahmedabad · Varanasi · Rishikesh · Manali · Shimla · Leh · Darjeeling · Shillong · Coorg · Mysore · Amritsar · Andaman · Pondicherry

**International**

Bangkok · Bali · Dubai · Singapore · Maldives · Kathmandu

---

### 🔎 Fuzzy Destination Matching

TripMind is designed to handle imperfect user input.

For example:

```text
a trip to ahemdabad
```

is correctly interpreted as:

```text
Ahmedabad
```

The planner uses fuzzy matching rather than requiring users to enter an exact destination name.

It also avoids silently recommending unrelated destinations when a user explicitly requests a destination that is not supported.

---

### 💰 Budget-Aware Planning

TripMind considers the complete trip cost instead of recommending a destination independently of the user's budget.

The planner evaluates:

```text
Flight Cost
      +
Hotel Cost × Number of Nights
      =
Estimated Trip Cost
```

Destinations are ranked using:

1. Whether they fit within the budget
2. How closely they match the requested preferences
3. Overall estimated cost

---

### ✈️ Flight & Hotel Selection

For every generated trip, TripMind selects:

* Departure city
* Destination
* Flight option
* Departure date
* Hotel
* Hotel rating
* Hotel price per night
* Estimated total cost

The system prioritizes options that satisfy the user's budget while maintaining destination relevance.

---

### 🗺️ Day-by-Day Itinerary

Every generated trip includes a structured itinerary.

Example:

```text
Day 1
Arrival + hotel check-in + local exploration

Day 2
Major attractions + local food experience

Day 3
Adventure / sightseeing activities

Day 4
Cultural exploration + shopping

Day 5
Relaxation + departure
```

---

### 🔄 Multi-Turn Trip Refinement

TripMind supports conversational trip modifications.

After receiving a plan, users can say:

```text
Make it cheaper.
```

```text
Try mountains instead.
```

```text
Make the trip longer.
```

```text
Show me somewhere else.
```

The planner uses the previous conversation context to generate an updated plan.

---

### 🪪 Rich Trip Cards

Generated plans are presented as interactive travel cards containing:

* 🛫 Route
* ✈️ Flight
* 🏨 Hotel
* 💰 Total cost
* 📅 Number of nights
* 🗓️ Day-by-day itinerary
* 🔎 Alternative destinations
* 📄 Download PDF
* 🗺️ Show map

This makes the planning experience feel closer to a real travel product rather than a traditional chatbot.

---

### 📄 PDF Itinerary Export

Users can generate a downloadable PDF itinerary directly from their trip.

PDF generation is handled server-side using **FPDF2**.

---

### 🗺️ Interactive Maps

Each destination can be visualized using **OpenStreetMap**.

No paid map API key is required.

---

### 👤 Authentication

TripMind includes secure user authentication using:

* JWT
* bcrypt password hashing
* Protected API routes

Users can:

* Register
* Log in
* View their profile
* Save trips
* View previous trips
* Cancel trips
* Manage preferences

---

### ⚙️ Personalized Settings

Users can save travel preferences such as:

* Home city
* Budget style

The saved home city can be used as the default departure location when planning future trips.

---

### 🏠 Personalized My Trips Dashboard

Every successful trip plan is automatically saved.

Users can view their previous trips from:

**My Trips**

They can also:

* Review trip details
* Cancel bookings
* Download itineraries
* View destination maps

---

# 🧠 How the AI Planner Works

TripMind uses a modular planning engine implemented in:

```text
backend/app/planner.py
```

The planning pipeline can be summarized as:

```text
User Message
     │
     ▼
Natural Language Parsing
     │
     ├── Budget
     ├── Duration
     ├── Month / Season
     ├── Origin
     ├── Destination
     └── Travel Vibes
     │
     ▼
Destination Matching
     │
     ▼
Destination Scoring
     │
     ▼
Flight Selection
     │
     ▼
Hotel Selection
     │
     ▼
Budget Validation
     │
     ▼
Destination Ranking
     │
     ▼
Itinerary Generation
     │
     ▼
Trip Saved to Database
     │
     ▼
Interactive Trip Card
```

### Destination Scoring

Each destination receives a relevance score based on:

```text
Vibe Match
    +
Season Match
    +
User Preferences
    +
Budget Compatibility
```

For example, a request containing:

```text
mountains + snow + December
```

will give higher scores to destinations such as:

```text
Manali
Shimla
Leh
Darjeeling
```

rather than beach destinations.

---

# 🤖 Deterministic AI + Optional LLM

TripMind separates **decision-making** from **language generation**.

The core planning logic is deterministic and handled by Python.

This means the system can:

* Parse requests
* Match destinations
* Calculate budgets
* Select flights
* Select hotels
* Rank alternatives
* Generate itineraries

without depending on an external LLM.

An optional **Groq-compatible LLM API** can be enabled to improve the natural-language presentation of generated responses.

This architecture provides an important advantage:

> **If the LLM is unavailable, the travel planner continues to work using the built-in planning engine.**

---

# 🏗️ System Architecture

```text
                    ┌──────────────────────┐
                    │      Frontend        │
                    │ HTML / CSS / JS      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      FastAPI         │
                    │    REST Backend      │
                    └──────────┬───────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
      ┌─────────────┐   ┌──────────────┐  ┌──────────────┐
      │    Auth     │   │ Trip Planner │  │   Booking    │
      │ JWT/bcrypt  │   │    Engine    │  │   Service    │
      └─────────────┘   └──────┬───────┘  └──────┬───────┘
                               │                 │
                               ▼                 ▼
                        ┌──────────────┐   ┌──────────────┐
                        │   Catalog    │   │   Database   │
                        │ Destinations │   │   SQLite /   │
                        │ Flights      │   │   PostgreSQL │
                        │ Hotels       │   └──────────────┘
                        └──────────────┘
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
        ┌──────────────┐              ┌──────────────┐
        │  FPDF2 PDF   │              │ OpenStreetMap│
        │   Export     │              │     Maps     │
        └──────────────┘              └──────────────┘
```

---

# 🛠️ Tech Stack

| Layer                  | Technology                 |
| ---------------------- | -------------------------- |
| Frontend               | HTML5, CSS3, JavaScript    |
| Backend                | Python, FastAPI            |
| Database               | SQLite / PostgreSQL        |
| ORM                    | SQLAlchemy                 |
| Authentication         | JWT + bcrypt               |
| Validation             | Pydantic                   |
| PDF Generation         | FPDF2                      |
| Maps                   | OpenStreetMap              |
| Optional LLM           | Groq-compatible OpenAI API |
| Server                 | Uvicorn                    |
| Environment Management | python-dotenv              |

---

# 📁 Project Structure

```text
TripMind/
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── runtime.txt
│   ├── .env.example
│   │
│   └── app/
│       ├── __init__.py
│       ├── database.py
│       ├── auth.py
│       ├── schemas.py
│       ├── seed_data.py
│       ├── catalog.py
│       ├── planner.py
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   └── db_models.py
│       │
│       └── routes/
│           ├── __init__.py
│           ├── auth_routes.py
│           ├── chat_routes.py
│           └── booking_routes.py
│
├── frontend/
│   ├── landing.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── chat.html
│   ├── trips.html
│   ├── settings.html
│   ├── api.js
│   ├── style.css
│   └── landing.css
│
├── run.bat
├── run.sh
├── .gitignore
└── README.md
```

---

# 🚀 Getting Started

## Prerequisites

Recommended:

```text
Python 3.12+
Git
```

Python 3.12 is recommended because it has broad package compatibility with the current dependency stack.

Check your Python version:

### Windows

```bash
py -3.12 --version
```

### macOS / Linux

```bash
python3.12 --version
```

---

# ⚡ Quick Start

Clone the repository:

```bash
git clone <your-repository-url>
cd TripMind
```

### Windows

```bash
cd backend
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### macOS / Linux

```bash
cd backend
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open:

```text
http://localhost:8000
```

API documentation:

```text
http://localhost:8000/docs
```

---

# 🖥️ One-Command Run

The project also includes startup scripts.

### Windows

From the project root:

```bash
run.bat
```

### macOS / Linux

```bash
./run.sh
```

These scripts simplify environment creation, dependency installation, and application startup.

---

# 🌱 Automatic Database Seeding

TripMind automatically initializes its database and seeds the required travel data when the application starts.

The shared destination catalog is maintained in:

```text
backend/app/catalog.py
```

This acts as the **single source of truth** for destination metadata.

The catalog contains information such as:

```text
Destination
Vibes
Best Travel Months
Coordinates
Estimated Flight Cost
Hotel Cost
Destination Guide
```

This prevents the planner and database seed data from becoming inconsistent.

---

# 🔌 API Reference

| Method | Endpoint                | Description              |
| ------ | ----------------------- | ------------------------ |
| `POST` | `/auth/register`        | Register a new user      |
| `POST` | `/auth/login`           | Authenticate user        |
| `GET`  | `/auth/me`              | Get current user         |
| `POST` | `/chat`                 | Generate a trip plan     |
| `GET`  | `/bookings`             | Retrieve saved trips     |
| `POST` | `/bookings/{id}/cancel` | Cancel a trip            |
| `GET`  | `/bookings/{id}/pdf`    | Download trip PDF        |
| `GET`  | `/stats`                | Retrieve trip statistics |
| `PUT`  | `/preferences`          | Update user preferences  |
| `GET`  | `/health`               | Health check             |

Protected endpoints use:

```http
Authorization: Bearer <JWT_TOKEN>
```

The frontend handles token management automatically.

---

# 💬 Example Queries

TripMind can understand requests such as:

### Budget-based

```text
Plan a 5-day trip from Delhi under ₹30,000.
```

### Seasonal

```text
Somewhere warm in December from Mumbai.
```

### Destination-specific

```text
Plan a trip to Ahmedabad for 4 nights.
```

### Preference-based

```text
I want a quiet mountain vacation for 6 days.
```

### International

```text
Find me a budget trip to Bangkok from Delhi.
```

### Conversational refinement

```text
Make it cheaper.
```

```text
Try mountains instead.
```

```text
Give me another option.
```

```text
Make it longer.
```

---

# 🔐 Environment Variables

LLM integration is optional.

Create a `.env` file inside:

```text
backend/.env
```

Example:

```env
OPENAI_API_KEY=your_groq_api_key
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.1-8b-instant
```

The LLM is only used to improve response wording. Core trip selection does not depend on it.

### ⚠️ Security

Never commit:

```text
.env
```

to GitHub.

If an API key has ever been exposed publicly, revoke and regenerate it immediately.

---

# ☁️ Deployment

TripMind is designed to run as a **single web service** because FastAPI serves both the API and frontend.

A simple deployment architecture is:

```text
GitHub
   │
   ▼
Render / Cloud Platform
   │
   ▼
FastAPI + Frontend
   │
   ├── API
   ├── Web UI
   └── Database
```

For a demo deployment, SQLite can be used.

For persistent production data, PostgreSQL is recommended.

---

# 📊 Current Capabilities

| Capability                     | Status |
| ------------------------------ | ------ |
| Natural-language trip requests | ✅      |
| Budget parsing                 | ✅      |
| Duration parsing               | ✅      |
| Month/season detection         | ✅      |
| Origin detection               | ✅      |
| Destination matching           | ✅      |
| Fuzzy destination matching     | ✅      |
| Destination scoring            | ✅      |
| Flight selection               | ✅      |
| Hotel selection                | ✅      |
| Budget ranking                 | ✅      |
| Alternative destinations       | ✅      |
| Multi-turn edits               | ✅      |
| Day-by-day itinerary           | ✅      |
| User authentication            | ✅      |
| Saved trips                    | ✅      |
| Trip cancellation              | ✅      |
| PDF export                     | ✅      |
| Interactive maps               | ✅      |
| User preferences               | ✅      |
| Optional LLM enhancement       | ✅      |
| Real-time flight API           | 🔜     |
| Real-time hotel API            | 🔜     |

---

# 🎓 Project Highlights

TripMind demonstrates practical implementation of several software engineering and AI concepts:

### Artificial Intelligence

* Natural-language understanding
* Fuzzy matching
* Preference-based ranking
* Recommendation systems
* Context-aware conversational refinement

### Backend Engineering

* REST API architecture
* FastAPI
* Modular Python backend
* SQLAlchemy ORM
* Authentication and authorization
* Database seeding
* PDF generation

### Full-Stack Development

* Responsive frontend
* API integration
* Authentication flow
* Interactive chat interface
* Persistent user trips
* Maps and document generation

### Product Thinking

The project focuses on reducing the complexity of travel planning by combining multiple user tasks into a single conversational workflow.

---

# 🚧 Future Improvements

TripMind can be extended into a more production-grade travel platform by adding:

### ✈️ Real-Time Travel Data

Integrate APIs for:

* Live flight prices
* Hotel availability
* Weather
* Transportation

This would replace the current estimated catalog pricing.

### 🧠 Advanced LLM Agent

Introduce an LLM-based planning agent capable of:

* Tool calling
* Destination research
* Real-time API retrieval
* Itinerary reasoning
* Dynamic re-planning

### 📍 More Personalized Recommendations

Use historical user interactions to learn:

```text
Preferred destinations
Budget patterns
Travel styles
Previous trips
```

and improve future recommendations.

### 🌦️ Weather-Aware Planning

Use live weather data to modify recommendations and itineraries dynamically.

### 💳 Cost Optimization

Add optimization for:

```text
Flight + Hotel + Activities + Transportation
```

rather than only flight and hotel.

### 👥 Collaborative Trips

Allow multiple users to:

* Create shared trips
* Vote on destinations
* Edit itineraries
* Split expenses

---

# 🧪 Example User Journey

```text
1. User opens TripMind
          ↓
2. Creates an account
          ↓
3. Enters:
   "Warm destination in December,
   5 days, under ₹30,000 from Delhi"
          ↓
4. Planner extracts requirements
          ↓
5. Destinations are scored
          ↓
6. Best destination is selected
          ↓
7. Flight + hotel are selected
          ↓
8. Total cost is calculated
          ↓
9. Day-by-day itinerary is generated
          ↓
10. Trip is saved automatically
          ↓
11. User can download PDF
          ↓
12. User can view destination on map
          ↓
13. User can refine the trip conversationally
```

---

# 🏆 Why TripMind?

TripMind is more than a simple travel chatbot.

It combines:

> **Natural Language + Recommendation Logic + Budget Optimization + Full-Stack Development + Authentication + Database Persistence + PDF Generation + Maps**

into one modular application.

The architecture also deliberately separates the **planning logic from language generation**, making the system more reliable and easier to extend with real-world APIs or advanced LLM agents in the future.

---

# 👩‍💻 Author

**Manvi Sharma**

B.Tech — Computer Science Engineering
Specialization in Artificial Intelligence & Machine Learning

Interested in:

* Artificial Intelligence
* Machine Learning
* Generative AI
* Full-Stack Development
* Intelligent Product Development

---

## ⭐ If you found TripMind interesting

Give the repository a ⭐ and feel free to explore, improve, and extend the project.

```text
TripMind
├── Understand your request
├── Find the right destination
├── Optimize your budget
├── Build your itinerary
└── Save your journey ✈️
```
