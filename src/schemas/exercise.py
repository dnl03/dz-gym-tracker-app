from sqlmodel import SQLModel



class ExerciseRead(SQLModel):
    id: int
    name: str
    description: str
