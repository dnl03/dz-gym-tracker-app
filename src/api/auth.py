from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from datetime import datetime, timedelta
import secrets

from db.session import get_session
from db.user_repository import get_user_by_email
from db.verification_repository import get_verification_code_by_user_id, delete_verification_code
from models.user import User, UserStatusEnum
from models.verification_code import VerificationCode
from schemas.user import UserCreate, UserRead
from schemas.verification_code import VerificationCodeRequest
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

    vc = VerificationCode(
        user_id = user.id,
        code = secrets.token_hex(3).upper(),
        expires_at = datetime.now() + timedelta(hours=1)  # Code valid for 1 hour
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    session.add(vc)
    session.commit()
    session.refresh(vc)

    return user


@router.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
    ):


    user = get_user_by_email(session, form_data.username)
    if user and user.blocked_until and user.blocked_until > datetime.now():
        raise HTTPException(status_code=429, detail=f"User is blocked until {user.blocked_until}")

    if not user or not verify_password(form_data.password, user.password_hash):
        if user:
            user.failed_login_try += 1
            if user.failed_login_try >= 5:
                user.blocked_until = datetime.now() + timedelta(minutes=15)
                session.add(user)
                session.commit()
                raise HTTPException(status_code=403, detail="User is blocked due to too many failed login attempts")

        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.status != UserStatusEnum.VERIFIED:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Twoje konto nie zostało jeszcze zweryfikowane!")

    token = create_access_token(subject=str(user.id))
    return {"access_token": token, "token_type": "bearer"}


@router.post("/verify")
def verify_user(verification_code: VerificationCodeRequest, session: Session = Depends(get_session)):

    if (user := get_user_by_email(session, verification_code.email)) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid user or verification code")

    if (vc := get_verification_code_by_user_id(session, user.id, verification_code.code)) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid user or verification code")


    if datetime.now() > vc.expires_at:
        delete_verification_code(session, vc)
        session.commit()
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Kod weryfikacyjny wygasł!")
    
    user.status = UserStatusEnum.VERIFIED
    session.add(user)
    delete_verification_code(session, vc)
    session.commit()
    return {"detail": "Konto zostało pomyślnie zweryfikowane!"}
    

@router.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user
