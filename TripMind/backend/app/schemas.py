"""
app/schemas.py
--------------
Pydantic models describe the JSON that goes in and out of the API. FastAPI uses
them to validate requests automatically and to build the /docs page.
"""

from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr


# ---- Auth ----
class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str] = None
    preferences: dict = {}

    class Config:
        from_attributes = True


# ---- Chat ----
class ChatIn(BaseModel):
    message: str
    conversation_id: Optional[int] = None


class ChatOut(BaseModel):
    conversation_id: int
    reply: str
    booking_id: Optional[int] = None
    itinerary: Optional[Any] = None


# ---- Bookings ----
class BookingOut(BaseModel):
    id: int
    status: str
    total_price: float
    itinerary: Any
    created_at: Any

    class Config:
        from_attributes = True


# ---- Preferences ----
class PreferencesIn(BaseModel):
    home_city: Optional[str] = None
    budget_style: Optional[str] = None
