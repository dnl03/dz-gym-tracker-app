from sqlmodel import SQLModel
from core.validators import SetWeight, SetReps

class WorkoutSetCreate(SQLModel):
    reps: SetReps
    weight_kg: SetWeight