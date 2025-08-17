from typing import Annotated
from sqlmodel import Field
from decimal import Decimal
from datetime import datetime, date
import re


WeightKg = Annotated[Decimal, Field(gt=0, lt=200, max_digits=6, decimal_places=2)]
HeightCm = Annotated[Decimal, Field(gt=10, lt=300, max_digits=5, decimal_places=2)]
BodyFatPct = Annotated[Decimal, Field(gt=0, lt=70, max_digits=5, decimal_places=2)]
CircuitCm = Annotated[Decimal, Field(gt=10, max_digits=5, decimal_places=2)]


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