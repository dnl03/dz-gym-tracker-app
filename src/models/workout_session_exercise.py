from sqlmodel import SQLModel, Field
from datetime import datetime

from typing import Optional
import uuid


class WorkoutSessionExercise(SQLModel, table=True):
    __tablename__ = "workout_session_exercises"

    id: int = Field(default=None, primary_key=True)
    workout_session_id: uuid.UUID = Field(foreign_key="workout_sessions.id", index=True, nullable=False)
    exercise_id: int = Field(foreign_key="exercises.id", index=True, nullable=False)
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
