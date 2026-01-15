from pydantic import BaseModel, EmailStr, model_validator
from datetime import datetime
from typing import Literal

class CreateUserModelSchema(BaseModel):
    username: str
    email: EmailStr
    password: str
    confirm_password: str
    role: Literal["admin", "user"]

    @model_validator(mode="before")
    def check_passwords(cls, values):
        if values.get("password") != values.get("confirm_password"):
            raise ValueError("Passwords do not match")
        return values


class LoginUserModel(BaseModel):
    username: str
    password: str


class UserModelResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
