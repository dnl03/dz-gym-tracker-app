from sqlmodel import SQLModel

class WorkoutSessionExerciseCreate(SQLModel):
    exercise_id: int
