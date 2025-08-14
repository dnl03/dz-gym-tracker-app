import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field


class VerificationCode(SQLModel, table=True):
    __tablename__ = "verification_codes"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True, unique=True)
    code: str = Field(nullable=False, index=True, max_length=6)
    created_at: datetime = Field(default_factory=lambda: datetime.now(), nullable=False)
    expires_at: datetime = Field(nullable=False)
