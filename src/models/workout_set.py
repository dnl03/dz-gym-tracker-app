from sqlmodel import SQLModel, Field
import uuid
from decimal import Decimal
from datetime import datetime


class WorkoutSet(SQLModel, table=True):
    __tablename__ = "workout_sets"

    id: int = Field(default=None, primary_key=True)
    session_exercise_id: uuid.UUID = Field(foreign_key="workout_session_exercises.id", index=True, nullable=False)
    weight_kg: Decimal = Field(nullable=False)
    reps: int = Field(nullable=False)
    volume: Decimal = Field(nullable=False)
    intensity: Decimal = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)

