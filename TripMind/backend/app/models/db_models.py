"""
app/models/db_models.py
-----------------------
The database tables described as Python classes (SQLAlchemy ORM).

This was the main missing file: your main.py, auth.py and seed_data.py all do
`from app.models.db_models import ...`, but the file did not exist, so the whole
app failed to import. These classes match the schema already present in your
tripmind.db exactly, so nothing about your data changes.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship, declarative_base

# `Base` is what main.py calls Base.metadata.create_all(engine) on to make the
# tables, and what every model below inherits from.
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)   # bcrypt hash, never raw text
    name = Column(String)
    preferences = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversations = relationship("Conversation", back_populates="user")
    bookings = relationship("Booking", back_populates="user")


class Flight(Base):
    __tablename__ = "flights"

    id = Column(Integer, primary_key=True)
    airline = Column(String, nullable=False)
    origin = Column(String, nullable=False, index=True)
    destination = Column(String, nullable=False, index=True)
    departure_date = Column(String, nullable=False)   # ISO text e.g. "2026-09-14"
    price = Column(Float, nullable=False)
    duration_minutes = Column(Integer)
    stops = Column(Integer, default=0)


class Hotel(Base):
    __tablename__ = "hotels"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False, index=True)
    price_per_night = Column(Float, nullable=False)
    rating = Column(Float)
    amenities = Column(JSON, default=list)


class DestinationDoc(Base):
    __tablename__ = "destination_docs"

    id = Column(Integer, primary_key=True)
    city = Column(String, nullable=False, index=True)
    title = Column(String)
    content = Column(Text, nullable=False)


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation",
                            cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)      # "user" or "assistant"
    content = Column(Text, nullable=False)
    tool_calls = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    flight_id = Column(Integer, ForeignKey("flights.id"))
    hotel_id = Column(Integer, ForeignKey("hotels.id"))
    status = Column(String, default="confirmed")   # confirmed | cancelled
    total_price = Column(Float, nullable=False)
    itinerary = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="bookings")
