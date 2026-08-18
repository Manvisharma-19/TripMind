"""
app/seed_data.py
----------------
Fills the reference tables (flights, hotels, destination_docs) from the shared
catalog (app/catalog.py). Run standalone with:  python -m app.seed_data

Auto-refresh: if the catalog has grown since the DB was last seeded (e.g. we
added Ahmedabad and 17 other cities), this clears just the reference tables and
re-seeds them. Your users, conversations and bookings are left untouched —
bookings store their own itinerary JSON, so they keep displaying correctly.
"""
import random
from datetime import date, timedelta
from app.database import engine, SessionLocal
from app.models.db_models import Base, Flight, Hotel, DestinationDoc
from app.catalog import ORIGINS, DESTINATIONS

Base.metadata.create_all(bind=engine)

AIRLINES = ["IndiGo", "Air India", "Vistara", "SpiceJet", "Akasa Air"]


def _price(base, spread=0.2):
    return round(base * (1 + random.uniform(-spread, spread)), 2)


def seed():
    db = SessionLocal()
    try:
        have = db.query(Flight.destination).distinct().count()
        want = len(DESTINATIONS)
        # Seed if empty, or refresh if the catalog changed size.
        if db.query(Flight).count() > 0 and have >= want:
            print("Data already seeded, skipping.")
            return
        if db.query(Flight).count() > 0:
            print(f"Catalog grew ({have} -> {want} destinations); refreshing reference data...")
            db.query(Flight).delete()
            db.query(Hotel).delete()
            db.query(DestinationDoc).delete()
            db.commit()

        today = date.today()
        for origin in ORIGINS:
            for dest, (vibes, months, lat, lon, fbase, hbase, doc) in DESTINATIONS.items():
                if dest == origin:
                    continue
                for day_offset in range(1, 181, 6):     # ~6 months of dates
                    d = today + timedelta(days=day_offset)
                    db.add(Flight(
                        airline=random.choice(AIRLINES),
                        origin=origin, destination=dest,
                        departure_date=d.isoformat(),
                        price=_price(fbase),
                        duration_minutes=random.randint(75, 300),
                        stops=random.choice([0, 0, 0, 1]),
                    ))

        for dest, (vibes, months, lat, lon, fbase, hbase, doc) in DESTINATIONS.items():
            for tier, mult, rating in [("Budget", 0.65, 3.7), ("Comfort", 1.0, 4.3), ("Premium", 1.9, 4.7)]:
                db.add(Hotel(
                    name=f"{dest} {tier} Stay", city=dest,
                    price_per_night=_price(hbase * mult, 0.12), rating=rating,
                    amenities=["Wifi", "Breakfast"] + (["Pool", "AC"] if tier != "Budget" else [])
                              + (["Spa", "View"] if tier == "Premium" else []),
                ))
            db.add(DestinationDoc(city=dest, title=f"{dest} Travel Guide", content=doc))

        db.commit()
        print(f"Seed complete: {len(DESTINATIONS)} destinations, "
              f"{db.query(Flight).count()} flights, {db.query(Hotel).count()} hotels.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
