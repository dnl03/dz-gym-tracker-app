from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class Exercise(SQLModel, table=True):
    __tablename__ = "exercises"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, nullable=False, unique=True)
    description: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(), nullable=False)