from sqlmodel import SQLModel, Field
from pydantic import field_validator
from core.validators import non_empty_string_validation

class WorkoutSessionCreate(SQLModel):
    name: str = Field(max_length=50)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        return non_empty_string_validation(value)
