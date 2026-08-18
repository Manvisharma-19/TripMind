"""
app/routes/booking_routes.py
----------------------------
  GET  /bookings                 -> list my trips
  POST /bookings/{id}/cancel     -> cancel a trip
  GET  /bookings/{id}/pdf        -> download the itinerary as a PDF
  GET  /stats                    -> dashboard numbers
  PUT  /preferences              -> save home city / budget style
"""

import io
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from fpdf import FPDF

from app.database import get_db
from app.models.db_models import User, Booking
from app.auth import get_current_user
from app import schemas

router = APIRouter(tags=["bookings"])


@router.get("/bookings", response_model=list[schemas.BookingOut])
def list_bookings(db: Session = Depends(get_db),
                  user: User = Depends(get_current_user)):
    return db.query(Booking).filter(Booking.user_id == user.id) \
             .order_by(Booking.created_at.desc()).all()


@router.post("/bookings/{booking_id}/cancel")
def cancel_booking(booking_id: int, db: Session = Depends(get_db),
                   user: User = Depends(get_current_user)):
    booking = db.query(Booking).filter(
        Booking.id == booking_id, Booking.user_id == user.id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking.status = "cancelled"
    db.commit()
    return {"ok": True, "status": booking.status}


def _rupees(n):
    return "Rs " + format(int(round(n)), ",d")


@router.get("/bookings/{booking_id}/pdf")
def booking_pdf(booking_id: int, db: Session = Depends(get_db),
                user: User = Depends(get_current_user)):
    booking = db.query(Booking).filter(
        Booking.id == booking_id, Booking.user_id == user.id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    it = booking.itinerary or {}

    from fpdf.enums import XPos, YPos
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(True, margin=15)
    epw = pdf.w - pdf.l_margin - pdf.r_margin   # effective page width

    def row(text, size=11, style="", color=(19, 42, 70), h=7):
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", style, size)
        pdf.set_text_color(*color)
        pdf.multi_cell(epw, h, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # header band
    pdf.set_fill_color(19, 42, 70)
    pdf.rect(0, 0, pdf.w, 30, style="F")
    pdf.set_xy(pdf.l_margin, 10)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(250, 247, 241)
    pdf.cell(epw, 12, "TripMind  -  Itinerary",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_y(40)
    row(f"{it.get('origin','')}  to  {it.get('destination','')}", size=16, style="B")
    row(f"Status: {booking.status.title()}    Nights: {it.get('nights','')}    "
        f"Departs: {it.get('departure_date','')}", size=11, color=(90, 114, 144))
    pdf.ln(2)

    row("Flight", size=12, style="B")
    row(f"{it.get('airline','')}   -   {_rupees(it.get('flight_price', 0))}")
    pdf.ln(1)
    row("Hotel", size=12, style="B")
    row(f"{it.get('hotel_name','')}  (rating {it.get('hotel_rating','')})   -   "
        f"{_rupees(it.get('hotel_price_per_night', 0))}/night")
    pdf.ln(1)
    row("Day-by-day", size=12, style="B")
    for i, day in enumerate(it.get("days", []), 1):
        row(f"Day {i}: {day}")
    pdf.ln(2)
    row(f"Total: {_rupees(booking.total_price)}", size=14, style="B", color=(242, 166, 90))

    buf = io.BytesIO(bytes(pdf.output()))
    filename = f"tripmind_{it.get('destination','trip')}_{booking.id}.pdf"
    return StreamingResponse(buf, media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@router.get("/stats")
def stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    bookings = db.query(Booking).filter(Booking.user_id == user.id).all()
    confirmed = [b for b in bookings if b.status == "confirmed"]
    cities = sorted({b.itinerary.get("destination") for b in confirmed
                     if isinstance(b.itinerary, dict) and b.itinerary.get("destination")})
    return {"trips_planned": len(bookings), "confirmed": len(confirmed),
            "cancelled": len(bookings) - len(confirmed),
            "total_spent": sum(b.total_price for b in confirmed),
            "cities": cities, "name": user.name}


@router.put("/preferences", response_model=schemas.UserOut)
def update_prefs(data: schemas.PreferencesIn, db: Session = Depends(get_db),
                 user: User = Depends(get_current_user)):
    prefs = dict(user.preferences or {})
    if data.home_city is not None:
        prefs["home_city"] = data.home_city
    if data.budget_style is not None:
        prefs["budget_style"] = data.budget_style
    user.preferences = prefs
    db.commit()
    db.refresh(user)
    return user
