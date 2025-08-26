from sqlmodel import SQLModel
from typing import Optional
import uuid
from decimal import Decimal
from datetime import datetime

class OneRepMaxCreate(SQLModel):
    exercise_id: int
    weight: float
    video_url: Optional[str]


class OneRepMaxRead(SQLModel):
    id: uuid.UUID
    exercise_name: str
    weight: Decimal
    created_at: datetime