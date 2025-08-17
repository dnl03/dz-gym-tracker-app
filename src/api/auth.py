from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select

from datetime import datetime, timedelta
import secrets

from db.session import get_session
from db.user_repository import get_user_by_email
from db.verification_repository import get_verification_code_by_user_id, delete_verification_code
from db.password_reset_repository import get_reset_token, delete_reset_token, delete_tokens_by_user_id
from models.user import User, UserStatusEnum
from models.verification_code import VerificationCode
from models.password_reset_token import PasswordResetToken
from models.user_details import UserDetail

from schemas.user import UserCreate, UserRead
from schemas.verification_code import VerificationCodeRequest
from schemas.password_reset import ForgotPasswordRequest, ResetPasswordRequest

from core.security import hash_password, verify_password, create_access_token, create_token_and_hash, sha256_hex
from fastapi.security import OAuth2PasswordRequestForm
from core.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(data: UserCreate, session: Session = Depends(get_session)):
    if get_user_by_email(session, data.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Podany adres istnieje w bazie danych!")

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        birth_date=data.birth_date,
        gender=data.gender
    )

    vc = VerificationCode(
        user_id = user.id,
        code = secrets.token_hex(3).upper(),
        expires_at = datetime.now() + timedelta(hours=1)  # Code valid for 1 hour
    )
    user.user_details.append(
        UserDetail(
            user_id=user.id,
            weight_kg=data.weight_kg,
            height_cm=data.height_cm,
            bf_pct=data.bf_pct,
            biceps_cm=data.biceps_cm,
            waist_cm=data.waist_cm,
            thigh_cm=data.thigh_cm,
            chest_cm=data.chest_cm,
            calf_cm=data.calf_cm,
            avatar_url=data.avatar_url
        )
    )
    try:
        session.add(user)
        session.commit()
        session.refresh(user)

        session.add(vc)
        session.commit()
        session.refresh(vc)

    except Exception:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Błąd podczas tworzenia konta!")

    #TDOO: Send verification email with vc.code to user.email it is not important

    return {"detail": "Konto utworzone, sprawdź skrzynkę e-mail!"}


@router.post("/login", status_code=status.HTTP_200_OK)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
    ):


    user = get_user_by_email(session, form_data.username)
    if user and user.blocked_until and user.blocked_until > datetime.now():
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=f"Konto zablokowane do {user.blocked_until}")

    if not user or not verify_password(form_data.password, user.password_hash):
        if user:
            user.failed_login_try += 1
            failed_login_flag = user.failed_login_try >= 5

            if failed_login_flag:
                user.blocked_until = datetime.now() + timedelta(minutes=30)
                
            session.add(user)
            session.commit()
            if failed_login_flag:
                raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Konto zablokowane na 30 minut!")

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nieprawidłowy email lub hasło!")

    if user.status != UserStatusEnum.VERIFIED:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Twoje konto nie zostało jeszcze zweryfikowane!")

    token = create_access_token(subject=str(user.id))
    user.failed_login_try = 0
    user.blocked_until = None
    session.add(user)
    session.commit()
    return {"access_token": token, "token_type": "bearer"}


@router.post("/verify", status_code=status.HTTP_200_OK)
def verify_user(verification_code: VerificationCodeRequest, session: Session = Depends(get_session)):

    if (user := get_user_by_email(session, verification_code.email)) is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Niepoprawny kod aktywacyjny lub adres email!")

    if (vc := get_verification_code_by_user_id(session, user.id, verification_code.code)) is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Niepoprawny kod aktywacyjny lub adres email!")


    if datetime.now() > vc.expires_at:
        delete_verification_code(session, vc)
        session.commit()
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Kod weryfikacyjny wygasł!")
    
    user.status = UserStatusEnum.VERIFIED
    session.add(user)
    delete_verification_code(session, vc)
    session.commit()
    return {"detail": "Pomyślnie aktywowano konto!"}
    

@router.get("/me")
def read_me(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    latest_user_details = session.exec(
        select(UserDetail)
        .where(UserDetail.user_id == current_user.id)
        .order_by(UserDetail.created_at.desc())
        .limit(1)
    ).first()

    return UserRead(
        id=current_user.id,
        email=current_user.email,
        created_at=current_user.created_at,
        birth_date=current_user.birth_date,
        gender=current_user.gender,
        user_details=latest_user_details
    )



@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(data: ForgotPasswordRequest, session: Session = Depends(get_session)):
    user = get_user_by_email(session, data.email)
    if user:
        delete_tokens_by_user_id(session, user.id)
        plain_token, hash_token = create_token_and_hash()
        prt = PasswordResetToken(
            user_id=user.id,
            token=hash_token,
            expires_at=datetime.now() + timedelta(hours=1)
        )
        session.add(prt)
        session.commit()
        session.refresh(prt)
        # TODO: wysłać email z linkiem zawierającym plain_token
        print("localhost:3000/reset-password?token=" + plain_token)

    return {"detail": "Link do zresetowania hasła został wysłany na podany adres email!"}



@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(
        data: ResetPasswordRequest,
        token = Query(..., description="Token resetujący hasło"),
        session: Session = Depends(get_session)
    ):
    hash_token = sha256_hex(token)
    prt = get_reset_token(session, hash_token)

    if not prt or prt.used or prt.expires_at < datetime.now():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Wystąpił niezidentyfikowany problem z tokenem, spróbuj ponownie przypomnieć hasło!")

    user = session.get(User, prt.user_id)
    user.password_hash = hash_password(data.new_password)
    delete_reset_token(session, prt)
    session.add(user)
    session.commit()
    return {"detail": "Hasło zostało zmienione pomyślnie!"}