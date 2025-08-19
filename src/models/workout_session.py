from __future__ import annotations
import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field



class WorkoutSession(SQLModel, table=True):
    __tablename__ = "workout_sessions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True, nullable=False)
    name: str = Field(max_length=50, nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
