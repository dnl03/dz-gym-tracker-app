import enum
from datetime import datetime, date
from typing import Optional, TYPE_CHECKING
import uuid

from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr

if TYPE_CHECKING:
    from models.user_details import UserDetail


class GenderEnum(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"

class UserStatusEnum(str, enum.Enum):
    UNVERIFIED = "unverified"
    VERIFIED = "verified"

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: EmailStr = Field(nullable=False, unique=True, index=True)
    birth_date: date = Field(nullable=False)
    gender: GenderEnum = Field(nullable=False)
    password_hash: str = Field(nullable=False)
    status: UserStatusEnum = Field(nullable=False, default="unverified")
    created_at: datetime = Field(default_factory=lambda: datetime.now(), nullable=False)
    updated_at: Optional[datetime] = Field(default=None, nullable=True)
    blocked_until: Optional[datetime] = Field(default=None, nullable=True)
    failed_login_try: int = Field(default=0, nullable=False)

    user_details: list["UserDetail"] = Relationship(back_populates="user")
