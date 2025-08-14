
from datetime import date, datetime
import re
from decimal import Decimal
from typing import Optional, Annotated
import uuid

from sqlmodel import SQLModel
from pydantic import EmailStr, field_validator, Field

from models.user import GenderEnum, UserStatusEnum

Weight = Annotated[Decimal, Field(gt=0, lt=200, max_digits=6, decimal_places=2)]
Height = Annotated[Decimal, Field(gt=10, lt=300, max_digits=5, decimal_places=2)]


def birth_date_validation(value: date) -> date:
    if value > datetime.now().date():
        raise ValueError("Birth date cannot be in the future.")
    return value

def password_validation(value: str) -> str:
    password_regex = re.compile(r"^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$")
    if not password_regex.match(value):
        raise ValueError(
            "Password must be ≥8 chars, include uppercase, digit, and special char."
        )
    return value

class UserRead(SQLModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    email: EmailStr
    status: UserStatusEnum
    weight_kg: Decimal
    height_cm: Decimal
    birth_date: date
    gender: GenderEnum
    avatar_url: Optional[str] = None
    created_at: datetime


class UserCreate(SQLModel):
    email: EmailStr
    password: str
    weight_kg: Weight
    height_cm: Height
    birth_date: date
    gender: GenderEnum
    avatar_url: Optional[str] = None
    
    @field_validator("birth_date")
    @classmethod
    def bith_date_validator(cls, value: date) -> date:
        return birth_date_validation(value)

    # @field_validator("password")
    # @classmethod
    # def password_validator(cls, value: str) -> str:
    #     return password_validation(value)


class UserUpdate(SQLModel):
    password: Optional[str] = None
    weight_kg: Optional[Weight] = None
    height_cm: Optional[Height] = None
    birth_date: Optional[date] = None
    avatar_url: Optional[str] = None

    @field_validator("birth_date")
    @classmethod
    def bith_date_validator(cls, value: Optional[date]) -> date:
        if value is None:
            return value
        return birth_date_validation(value)

    @field_validator("password")
    @classmethod
    def password_validator(cls, value: Optional[str]) -> str:
        if value is None:
            return value
        return password_validation(value)
