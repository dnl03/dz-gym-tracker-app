from sqlmodel import SQLModel
from pydantic import EmailStr, field_validator



class VerificationCodeRequest(SQLModel):
    email: EmailStr
    code: str

    @field_validator("code")
    @classmethod
    def validate_code_length(cls, value: str) -> str:
        if len(value) != 6:
            raise ValueError("Verification code must be exactly 6 characters long")
        return value