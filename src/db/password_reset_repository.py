from sqlmodel import Session, select

from models.password_reset_token import PasswordResetToken
from typing import Optional
import uuid


def get_reset_token(session: Session, token: str) -> Optional[PasswordResetToken]:
    stmt = select(PasswordResetToken).where(PasswordResetToken.token == token)
    return session.exec(stmt).first()


def delete_tokens_by_user_id(session: Session, user_id: uuid.UUID) -> None:
    stmt = select(PasswordResetToken).where(PasswordResetToken.user_id == user_id)
    tokens = session.exec(stmt).all()
    for token in tokens:
        session.delete(token)
    session.commit()


def delete_reset_token(session: Session, prt: PasswordResetToken) -> None:
    session.delete(prt)
    session.commit()