import uuid
from sqlmodel import SQLModel, Field

from typing import Optional
from datetime import datetime
from decimal import Decimal


class OneRepMax(SQLModel, table=True):
    __tablename__ = "one_rep_maxes"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    exercise_id: int = Field(foreign_key="exercises.id", nullable=False, index=True)
    weight: Decimal = Field(nullable=False)
    video_url: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
