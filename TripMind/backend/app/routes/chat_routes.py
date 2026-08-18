"""
app/routes/chat_routes.py
-------------------------
  POST /chat  { message, conversation_id? }  ->  { conversation_id, reply, booking_id }

Supports multi-turn refinement: the previous plan's context is stored on the last
assistant message (in its tool_calls field) and fed back in, so a follow-up like
"make it cheaper" edits the previous trip instead of starting fresh.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import User, Conversation, Message, Booking
from app.auth import get_current_user
from app.planner import plan_trip, polish_reply
from app import schemas

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=schemas.ChatOut)
def chat(data: schemas.ChatIn, db: Session = Depends(get_db),
         user: User = Depends(get_current_user)):

    conv = None
    if data.conversation_id:
        conv = db.query(Conversation).filter(
            Conversation.id == data.conversation_id,
            Conversation.user_id == user.id).first()
    if conv is None:
        conv = Conversation(user_id=user.id, title=data.message[:40])
        db.add(conv)
        db.commit()
        db.refresh(conv)

    # Pull the context saved on the most recent assistant message (multi-turn).
    prev_context = None
    last_assistant = db.query(Message).filter(
        Message.conversation_id == conv.id, Message.role == "assistant") \
        .order_by(Message.id.desc()).first()
    if last_assistant and last_assistant.tool_calls:
        prev_context = last_assistant.tool_calls

    db.add(Message(conversation_id=conv.id, role="user", content=data.message))
    db.commit()

    result = plan_trip(db, data.message, prev_context=prev_context,
                       user_prefs=user.preferences or {})
    reply_text = polish_reply(result["reply"], data.message)

    booking_id = None
    if result.get("best"):
        best = result["best"]
        booking = Booking(user_id=user.id, flight_id=best["flight"].id,
                          hotel_id=best["hotel"].id, status="confirmed",
                          total_price=best["total"], itinerary=result["itinerary"])
        db.add(booking)
        db.commit()
        db.refresh(booking)
        booking_id = booking.id

    # Store the planning context on the assistant message for the next turn.
    db.add(Message(conversation_id=conv.id, role="assistant", content=reply_text,
                   tool_calls=result.get("context")))
    db.commit()

    return {"conversation_id": conv.id, "reply": reply_text, "booking_id": booking_id,
            "itinerary": result.get("itinerary")}
