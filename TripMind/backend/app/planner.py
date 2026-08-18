"""
app/planner.py
--------------
Turns a message into a trip. Rule-based + offline (always works), with optional
LLM reword. Reads all destinations from app/catalog.py.

Key fixes in this version:
  * Recognises 27 destinations (was 9) incl. Ahmedabad, Agra, Dubai, Maldives...
  * Fuzzy matching: "ahemdabad" -> Ahmedabad, "manalli" -> Manali.
  * Honest fallback: if you name a place we don't cover, it SAYS so and lists
    what it can plan, instead of silently returning a random city.
  * Multi-turn edits, map coordinates and preference-awareness are kept.
"""

import os
import re
import json
import difflib
import urllib.request
from datetime import datetime

from app.models.db_models import Flight, Hotel, DestinationDoc
from app.catalog import DESTINATION_META, DEST_NAMES, ORIGINS

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11,
    "december": 12, "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7,
    "aug": 8, "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}
SEASON_HINTS = {"winter": 12, "summer": 5, "monsoon": 7, "autumn": 10, "spring": 3}

ORIGIN_LOWER = {o.lower(): o for o in ORIGINS}
ORIGIN_LOWER["bengaluru"] = "Bangalore"
DEST_LOWER = {n.lower(): n for n in DEST_NAMES}

# quick synonyms -> destination
SYNONYMS = {"kerala": "Alleppey", "ladakh": "Leh", "taj": "Agra",
            "tajmahal": "Agra", "backwaters": "Alleppey", "andamans": "Andaman"}

# every vibe word we know (used to tell a "vibe" apart from a place name)
ALL_VIBES = set()
for _m in DESTINATION_META.values():
    ALL_VIBES |= set(_m["vibes"])

STOPWORDS = {"a", "an", "the", "some", "somewhere", "trip", "holiday", "vacation",
             "place", "places", "spot", "go", "going", "get", "away", "break",
             "me", "my", "please", "want", "like", "for", "from", "and", "with",
             "days", "day", "nights", "night", "week", "weekend"} | ALL_VIBES \
             | set(MONTHS) | set(SEASON_HINTS)

VIBE_SWITCHES = {
    "mountains": "mountains", "mountain": "mountains", "snow": "snow",
    "beach": "beach", "beaches": "beach", "hills": "hills", "heritage": "heritage",
    "forts": "forts", "backwater": "backwater", "backwaters": "backwater",
    "island": "island", "romantic": "romantic", "lakes": "lakes", "quiet": "quiet",
    "party": "party", "nightlife": "nightlife", "adventure": "adventure",
    "temples": "temples", "city": "city", "warm": "warm", "desert": "desert",
    "luxury": "luxury", "spiritual": "spiritual", "tea": "tea", "coffee": "coffee",
}


def _resolve(token, pool_lower, cutoff):
    token = token.lower().strip()
    if token in pool_lower:
        return pool_lower[token]
    m = difflib.get_close_matches(token, list(pool_lower.keys()), n=1, cutoff=cutoff)
    return pool_lower[m[0]] if m else None


def _find_destination(text):
    """Return (destination, unknown_place). Exactly one is non-None, or both None."""
    t = text.lower()
    words = re.findall(r"[a-z]+", t)

    # 1) synonyms
    for syn, dest in SYNONYMS.items():
        if re.search(rf"\b{syn}\b", t):
            return dest, None

    # 2) exact / fuzzy over single words and bigrams (high cutoff to avoid noise)
    candidates = words + [f"{a} {b}" for a, b in zip(words, words[1:])]
    for c in candidates:
        if c in STOPWORDS:
            continue
        d = _resolve(c, DEST_LOWER, cutoff=0.86)
        if d:
            return d, None

    # 3) explicit "to/in/visit/see X" slot -> if it's a real word but not a place
    #    we know, treat it as an UNKNOWN place and be honest about it.
    m = re.search(r"\b(?:to|in|visit|visiting|see|explore|for)\s+([a-z]+)(?:\s+([a-z]+))?", t)
    if m:
        phrase = " ".join([w for w in m.groups() if w])
        toks = phrase.split()
        if not any(w in STOPWORDS or w in ALL_VIBES for w in toks):
            d = _resolve(phrase, DEST_LOWER, cutoff=0.72) or _resolve(toks[-1], DEST_LOWER, cutoff=0.78)
            if d:
                return d, None
            if len(toks[-1]) >= 4:
                return None, toks[-1].title()
    return None, None


def parse_request(text):
    t = text.lower()

    budget = None
    m = re.search(r"(?:rs\.?|₹|inr|budget|under|below|around)\s*([\d,]+)\s*(k)?", t)
    if not m:
        m = re.search(r"([\d,]+)\s*(k)\b", t)
    if m:
        num = int(m.group(1).replace(",", ""))
        budget = num * 1000 if m.group(2) == "k" else num
    elif re.search(r"\b(\d{4,6})\b", t):
        budget = int(re.search(r"\b(\d{4,6})\b", t).group(1))

    nights = None
    m = re.search(r"(\d+)\s*nights?", t)
    if m:
        nights = int(m.group(1))
    else:
        m = re.search(r"(\d+)\s*days?", t)
        if m:
            nights = max(1, int(m.group(1)) - 1)

    month = None
    for word, num in MONTHS.items():
        if re.search(rf"\b{word}\b", t):
            month = num
            break
    if month is None:
        for word, num in SEASON_HINTS.items():
            if word in t:
                month = num
                break

    origin = None
    m = re.search(r"from\s+([a-zA-Z]+)", t)
    if m:
        origin = _resolve(m.group(1), ORIGIN_LOWER, cutoff=0.84)
    if origin is None:
        for o_low, o in ORIGIN_LOWER.items():
            if re.search(rf"\bfrom\s+{o_low}\b", t):
                origin = o

    named_dest, unknown_place = _find_destination(text)

    return {"budget": budget, "nights": nights, "month": month, "origin": origin,
            "named_dest": named_dest, "unknown_place": unknown_place,
            "vibe_words": list(set(re.findall(r"[a-z]+", t)))}


def detect_edits(text):
    t = text.lower()
    e = {"cheaper": False, "pricier": False, "longer": False,
         "shorter": False, "another": False, "new_vibes": []}
    if re.search(r"cheap|cheaper|less expensive|lower budget|save money|affordable", t):
        e["cheaper"] = True
    if re.search(r"luxur|pricier|nicer|more expensive|premium|upgrade|fancy", t):
        e["pricier"] = True
    if re.search(r"longer|more days|more nights|extend", t):
        e["longer"] = True
    if re.search(r"shorter|fewer days|fewer nights|less days", t):
        e["shorter"] = True
    if re.search(r"another|different place|somewhere else|other option|something else|instead", t):
        e["another"] = True
    for word, vibe in VIBE_SWITCHES.items():
        if re.search(rf"\b{word}\b", t):
            e["new_vibes"].append(vibe)
    return e


def score_destination(city, vibe_words, month):
    meta = DESTINATION_META.get(city)
    if not meta:
        return 0.0
    s = len(set(vibe_words) & set(meta["vibes"])) * 3
    if month and month in meta["good_months"]:
        s += 4
    if "warm" in vibe_words and "warm" in meta["vibes"]:
        s += 2
    return s


def _hotel_by_style(hotels, style):
    o = sorted(hotels, key=lambda h: h.price_per_night)
    if style == "comfort":
        return o[-1]
    if style == "budget":
        return o[0]
    return o[len(o) // 2]


def build_option(db, city, req):
    flights = db.query(Flight).filter(
        Flight.origin == req["origin"], Flight.destination == city).all()
    if not flights:
        return None

    def month_of(f):
        try:
            return datetime.strptime(f.departure_date, "%Y-%m-%d").month
        except Exception:
            return None

    if req["month"]:
        pref = [f for f in flights if month_of(f) == req["month"]]
        if pref:
            flights = pref
    flight = min(flights, key=lambda f: f.price)

    hotels = db.query(Hotel).filter(Hotel.city == city).all()
    if not hotels:
        return None

    chosen = None
    if req["budget"]:
        remaining = req["budget"] - flight.price
        aff = [h for h in hotels if h.price_per_night * req["nights"] <= remaining]
        if aff:
            chosen = max(aff, key=lambda h: h.rating or 0)
    if chosen is None:
        chosen = (min(hotels, key=lambda h: h.price_per_night) if req["budget"]
                  else _hotel_by_style(hotels, req.get("budget_style", "balanced")))

    total = flight.price + chosen.price_per_night * req["nights"]
    return {"city": city, "flight": flight, "hotel": chosen, "nights": req["nights"],
            "total": total,
            "within_budget": (req["budget"] is None) or (total <= req["budget"]),
            "score": score_destination(city, req["vibe_words"], req["month"])}


DAY_TEMPLATES = {
    "beach": ["Arrive, settle in, sunset by the water",
              "Beach day and water sports",
              "Explore the coast and local seafood",
              "Boat trip or island hop",
              "Cafe morning, last swim, depart"],
    "mountains": ["Arrive, acclimatise, easy walk",
                  "Main viewpoints and adventure activity",
                  "Day trip to a nearby valley or pass",
                  "Local market and hot food",
                  "Slow morning and departure"],
    "heritage": ["Arrive, check in, evening old-town walk",
                 "Forts, palaces and museums",
                 "Local food tour and bazaars",
                 "Day trip to a nearby monument",
                 "Souvenirs and departure"],
    "default": ["Arrive, check in and explore nearby",
                "Main sights and local food tour",
                "Nature / adventure day",
                "Relaxed morning, shopping, cafes",
                "Free morning and departure"],
}


def _theme_for(city):
    v = set(DESTINATION_META.get(city, {}).get("vibes", []))
    if v & {"beach", "island", "coastal"}:
        return "beach"
    if v & {"mountains", "hills", "snow"}:
        return "mountains"
    if v & {"heritage", "forts", "palaces", "monuments"}:
        return "heritage"
    return "default"


def build_itinerary_days(city, nights):
    days = DAY_TEMPLATES[_theme_for(city)]
    return [days[i] if i < len(days) else "Free day to relax or explore"
            for i in range(nights + 1)]


def _inr(n):
    return "\u20b9" + format(int(round(n)), ",d")


def _finalize(parsed, edits, prev, prefs):
    prev = prev or {}
    prefs = prefs or {}
    req = {
        "budget": parsed["budget"] if parsed["budget"] is not None else prev.get("budget"),
        "nights": parsed["nights"] if parsed["nights"] is not None else prev.get("nights"),
        "month": parsed["month"] if parsed["month"] is not None else prev.get("month"),
        "origin": parsed["origin"] or prev.get("origin"),
        "named_dest": parsed["named_dest"] or (None if edits["another"] or edits["new_vibes"]
                                               else prev.get("named_dest")),
        "vibe_words": list(parsed["vibe_words"]),
        "budget_style": prefs.get("budget_style", "balanced"),
    }
    if prev.get("vibe_words") and (edits["cheaper"] or edits["pricier"] or
                                   edits["longer"] or edits["shorter"] or edits["another"]):
        req["vibe_words"] = list(set(req["vibe_words"]) | set(prev["vibe_words"]))
    if edits["new_vibes"]:
        req["vibe_words"] = list(set(req["vibe_words"]) | set(edits["new_vibes"]))
        req["named_dest"] = None
    if not req["origin"]:
        req["origin"] = prefs.get("home_city") or "Delhi"
    if not req["nights"]:
        req["nights"] = 4
    ref = req["budget"] or prev.get("last_total")
    if edits["cheaper"] and ref:
        req["budget"] = int(ref * 0.8)
    if edits["pricier"] and ref:
        req["budget"] = int(ref * 1.35)
    if edits["longer"]:
        req["nights"] = min(req["nights"] + 2, 10)
    if edits["shorter"]:
        req["nights"] = max(req["nights"] - 1, 1)
    return req


def plan_trip(db, text, prev_context=None, user_prefs=None):
    parsed = parse_request(text)
    edits = detect_edits(text)
    is_followup = bool(prev_context)

    # Honest handling of a place we don't cover (only on a fresh request).
    if parsed["unknown_place"] and not parsed["named_dest"] and not is_followup \
            and not any(w in ALL_VIBES for w in parsed["vibe_words"]):
        sample = ", ".join(["Goa", "Jaipur", "Manali", "Kerala (Kochi)", "Udaipur",
                            "Andaman", "Bangkok", "Dubai"])
        return {"best": None, "itinerary": None, "context": {"req": {}},
                "reply": (f"I don't have travel data for {parsed['unknown_place']} yet, so I "
                          f"can't plan a real trip there.\n\nRight now I can plan {len(DEST_NAMES)} "
                          f"destinations, including: {sample}, and more.\n\nTell me a place from "
                          f"that list, or just describe a vibe (\u201cwarm beach\u201d, "
                          f"\u201csnowy mountains\u201d, \u201cheritage city\u201d) with a budget "
                          f"and I'll plan it.")}

    req = _finalize(parsed, edits, (prev_context or {}).get("req"), user_prefs)
    avoid = prev_context.get("destination") if (edits["another"] and prev_context) else None

    if req["named_dest"]:
        candidates = [req["named_dest"]]
    else:
        candidates = sorted(DEST_NAMES,
                            key=lambda c: score_destination(c, req["vibe_words"], req["month"]),
                            reverse=True)
        if avoid:
            candidates = [c for c in candidates if c != avoid]
        candidates = candidates[:6]

    options = [o for o in (build_option(db, c, req) for c in candidates) if o]
    options.sort(key=lambda o: (not o["within_budget"], -o["score"], o["total"],
                                -(o["hotel"].rating or 0)))
    if not options:
        return {"best": None, "itinerary": None, "context": {"req": req},
                "reply": f"I couldn't find flights from {req['origin']} for that. "
                         "Try a different departure city or a budget and vibe."}

    best = options[0]
    alts = options[1:3]
    days = build_itinerary_days(best["city"], best["nights"])
    meta = DESTINATION_META[best["city"]]
    doc = db.query(DestinationDoc).filter(DestinationDoc.city == best["city"]).first()
    highlight = (doc.content.split(". ")[0] + ".") if doc else ""

    itinerary = {
        "destination": best["city"], "origin": req["origin"],
        "airline": best["flight"].airline, "departure_date": best["flight"].departure_date,
        "nights": best["nights"], "hotel_name": best["hotel"].name,
        "hotel_rating": best["hotel"].rating, "flight_price": best["flight"].price,
        "hotel_price_per_night": best["hotel"].price_per_night,
        "total_price": best["total"], "within_budget": best["within_budget"],
        "days": days, "highlight": highlight, "lat": meta["lat"], "lon": meta["lon"],
        "alternatives": [{"city": a["city"], "total": a["total"],
                          "airline": a["flight"].airline, "nights": a["nights"]} for a in alts],
        "is_update": is_followup,
    }
    reply = compose_reply(req, best, alts, days, highlight, is_followup)
    context = {"req": {**req, "last_total": best["total"]}, "destination": best["city"]}
    return {"best": best, "itinerary": itinerary, "reply": reply, "context": context}


def compose_reply(req, best, alts, days, highlight, was_edit):
    b = best
    lead = ("Updated \u2014 here's a revised plan" if was_edit else "Here's a plan") \
        + f" for {b['nights']} nights in {b['city']} from {req['origin']}."
    lines = [lead]
    if highlight:
        lines.append(highlight)
    lines += ["",
        f"\u2708\ufe0f  Flight: {b['flight'].airline}, {req['origin']} \u2192 {b['city']} on "
        f"{b['flight'].departure_date} \u2014 {_inr(b['flight'].price)}",
        f"\U0001f3e8  Stay: {b['hotel'].name} (\u2605{b['hotel'].rating}) \u2014 "
        f"{_inr(b['hotel'].price_per_night)}/night \u00d7 {b['nights']} = "
        f"{_inr(b['hotel'].price_per_night * b['nights'])}",
        f"\U0001f4b0  Total: {_inr(b['total'])}" + ("" if b["within_budget"]
         else "  (slightly over budget \u2014 the closest I could get)"),
        "", "Day-by-day:"]
    lines += [f"  Day {i}: {d}" for i, d in enumerate(days, 1)]
    if alts:
        lines += ["", "Other options I considered:"]
        lines += [f"  \u2022 {a['city']} \u2014 {_inr(a['total'])} "
                  f"({a['nights']} nights, {a['flight'].airline})" for a in alts]
    lines += ["", "Saved to your Trips. You can say \u201cmake it cheaper\u201d, "
              "\u201ctry mountains instead\u201d, or \u201cmake it longer\u201d."]
    return "\n".join(lines)


def polish_reply(reply_text, user_msg):
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    base_url = os.getenv("LLM_BASE_URL", "").strip()
    model = os.getenv("LLM_MODEL", "").strip()
    if not (api_key and base_url and model):
        return reply_text
    try:
        payload = {"model": model, "temperature": 0.5, "messages": [
            {"role": "system", "content":
             "You are TripMind, a warm, concise travel planner. Rewrite the draft in a "
             "friendly voice. Keep ALL facts, prices, dates and the day-by-day list identical."},
            {"role": "user", "content": f"User asked: {user_msg}\n\nDraft:\n{reply_text}"}]}
        req = urllib.request.Request(base_url.rstrip("/") + "/chat/completions",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            return json.loads(resp.read())["choices"][0]["message"]["content"].strip() or reply_text
    except Exception:
        return reply_text
