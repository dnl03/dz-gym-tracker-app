from datetime import datetime

from sqlmodel import SQLModel, Field
import uuid



class PasswordResetToken(SQLModel, table=True):
    __tablename__ = "password_reset_tokens"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    token: str = Field(nullable=False, index=True, unique=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    expires_at: datetime = Field(nullable=False)
    used: bool = Field(default=False, nullable=False)
