from sqlmodel import SQLModel
from typing import Optional
from core.validators import SetWeight, SetReps
from decimal import Decimal
from datetime import datetime

class WorkoutSetCreate(SQLModel):
    reps: SetReps
    weight_kg: SetWeight


class WorkoutSetUpdate(SQLModel):
    reps: Optional[SetReps] = None
    weight_kg: Optional[SetWeight] = None



class WorkoutSetRead(SQLModel):
    id: int
    exercise_name: str
    reps: int
    weight_kg: Decimal
    volume: Decimal
    intensity: Decimal
    created_at: datetime

    class Config:
        from_attributes = True