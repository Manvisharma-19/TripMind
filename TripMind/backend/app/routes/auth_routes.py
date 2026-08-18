"""
app/routes/auth_routes.py
-------------------------
Account endpoints. These were missing, which is why `from app.routes import
auth_routes` failed. Uses your existing app/auth.py helpers (bcrypt + JWT).

  POST /auth/register  -> create an account, return a token
  POST /auth/login     -> log in, return a token
  GET  /auth/me        -> the current logged-in user
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import User
from app.auth import hash_password, verify_password, create_access_token, get_current_user
from app import schemas

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.TokenOut)
def register(data: schemas.RegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        name=data.name or data.email.split("@")[0],
        preferences={},
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"access_token": create_access_token(user.id)}


@router.post("/login", response_model=schemas.TokenOut)
def login(data: schemas.LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Wrong email or password")
    return {"access_token": create_access_token(user.id)}


@router.get("/me", response_model=schemas.UserOut)
def me(user: User = Depends(get_current_user)):
    return user
