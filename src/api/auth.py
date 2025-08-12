from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from db.session import get_session
from db.user_repository import get_user_by_email
from models.user import User
from schemas.user import UserCreate, UserRead
from core.security import hash_password, verify_password, create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from core.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(data: UserCreate, session: Session = Depends(get_session)):
    if get_user_by_email(session, data.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        weight_kg=data.weight_kg,
        height_cm=data.height_cm,
        birth_date=data.birth_date,
        gender=data.gender,
        avatar_url=data.avatar_url,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user  # FastAPI zmapuje do UserRead


@router.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),  # <-- bierze username+password z form-data
    session: Session = Depends(get_session),
):
    email = form_data.username
    password = form_data.password

    user = get_user_by_email(session, email)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(subject=str(user.id))
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user
