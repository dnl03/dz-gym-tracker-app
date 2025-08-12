import enum
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional
import uuid

from sqlmodel import SQLModel, Field
from pydantic import EmailStr


class GenderEnum(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"

class UserStatusEnum(str, enum.Enum):
    UNVERIFIED = "unverified"
    VERIFIED = "verified"

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    email: EmailStr = Field(nullable=False, unique=True, index=True)
    password_hash: str = Field(nullable=False)
    status: UserStatusEnum = Field(nullable=False, default="unverified")
    weight_kg: Decimal = Field(nullable=False)
    height_cm: Decimal = Field(nullable=False)
    birth_date: date = Field(nullable=False)
    gender: GenderEnum = Field(nullable=False)
    avatar_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Optional[datetime] = Field(default=None, nullable=True)
