from sqlmodel import SQLModel
from typing import Optional



class OneRepMaxCreate(SQLModel):
    exercise_id: int
    weight: float
    video_url: Optional[str]
