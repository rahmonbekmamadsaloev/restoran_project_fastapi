from pydantic import BaseModel, EmailStr, model_validator
from typing import Literal
from typing import Optional


class CreateUserModelSchema(BaseModel):
    username: str
    email: EmailStr
    password: str
    confirm_password: str
   

    @model_validator(mode="before")
    def check_passwords(cls, values):
        password = values.get("password")
        confirm_password = values.get("confirm_password")

        if password != confirm_password:
            raise ValueError("Passwords do not match")

        return values


class LoginUserModel(BaseModel):
    username: str
    password: str


class UserModelResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    model_config = {"from_attributes": True}
    


class UpdateUserProfileSchema(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    number: Optional[int] = None
    image_profile: Optional[str] = None

