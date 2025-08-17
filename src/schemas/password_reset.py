from sqlmodel import SQLModel
from pydantic import EmailStr


class ForgotPasswordRequest(SQLModel):
    email: EmailStr


class ResetPasswordRequest(SQLModel):
    new_password: str

    # @field_validator("new_password")
    # @classmethod
    # def password_validator(cls, value: str) -> str:
    #     return password_validation(value)