from sqlmodel import SQLModel, Field, Relationship
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from models.user import UserStatusEnum

if TYPE_CHECKING:
    from models.user import User


class UserDetail(SQLModel, table=True):
    __tablename__ = "user_details"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    weight_kg: Decimal = Field(nullable=False)
    height_cm: Decimal = Field(nullable=False)

    bf_pct: Decimal = Field(nullable=False)
    biceps_cm: Decimal = Field(nullable=False)
    waist_cm: Decimal = Field(nullable=False)
    thigh_cm: Decimal = Field(nullable=False)
    chest_cm: Decimal = Field(nullable=False)
    calf_cm: Decimal = Field(nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(), nullable=False)

    avatar_url: Optional[str] = Field(default=None)

    user: Optional["User"] = Relationship(back_populates="user_details")
