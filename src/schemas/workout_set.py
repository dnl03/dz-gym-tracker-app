from sqlmodel import SQLModel
from typing import Optional
from core.validators import SetWeight, SetReps

class WorkoutSetCreate(SQLModel):
    reps: SetReps
    weight_kg: SetWeight


class WorkoutSetUpdate(SQLModel):
    reps: Optional[SetReps] = None
    weight_kg: Optional[SetWeight] = None
