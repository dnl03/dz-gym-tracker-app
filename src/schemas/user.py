
from datetime import date, datetime
from typing import Optional
import uuid

from sqlmodel import SQLModel
from pydantic import EmailStr, field_validator, Field

from models.user import GenderEnum
from core.validators import (
    WeightKg,
    HeightCm,
    BodyFatPct,
    CircuitCm,
    birth_date_validation
)
from schemas.user_details import UserDetailsRead


class UserRead(SQLModel):
    model_config = {"from_attributes": True}
    id: uuid.UUID
    email: EmailStr
    birth_date: date
    gender: GenderEnum
    created_at: datetime
    user_details: Optional["UserDetailsRead"] = None


class UserCreate(SQLModel):
    email: EmailStr
    password: str
    birth_date: date
    gender: GenderEnum

    # User details
    weight_kg: WeightKg
    height_cm: HeightCm

    bf_pct: BodyFatPct = Field(nullable=False)
    biceps_cm: CircuitCm = Field(nullable=False)
    waist_cm: CircuitCm = Field(nullable=False)
    chest_cm: CircuitCm = Field(nullable=False)
    thigh_cm: CircuitCm = Field(nullable=False)
    calf_cm: CircuitCm = Field(nullable=False)
    avatar_url: Optional[str] = Field(default=None, nullable=True)
    
    @field_validator("birth_date")
    @classmethod
    def bith_date_validator(cls, value: date) -> date:
        return birth_date_validation(value)

    # @field_validator("password")
    # @classmethod
    # def password_validator(cls, value: str) -> str:
    #     return password_validation(value)
