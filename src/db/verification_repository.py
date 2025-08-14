from sqlmodel import Session, select
from uuid import UUID
from typing import Optional
from models.verification_code import VerificationCode


def get_verification_code_by_user_id(session: Session, user_id: UUID, code: str) -> Optional[VerificationCode]:
    statement = select(VerificationCode).where(
        VerificationCode.user_id == user_id,
        VerificationCode.code == code
    )
    result = session.exec(statement).first()
    return result


def delete_verification_code(session: Session, ver: VerificationCode) -> None:
    session.delete(ver)