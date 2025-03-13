from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Annotated, List
from pydantic.types import StringConstraints
from datetime import datetime
from sqlmodel import Field
from db.models import UserRole
import uuid, re

UsernameType = Annotated[
    str, StringConstraints(min_length=3, max_length=50, pattern=r"^[\w.@+-]+$")
]
PasswordType = Annotated[str, StringConstraints(min_length=8, max_length=100)]
PASSWORD_REGEX = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"


# Schema for User Registration
class UserRegister(BaseModel):
    username: UsernameType
    email: EmailStr
    password: PasswordType

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if not re.match(PASSWORD_REGEX, value):
            raise ValueError(
                "Password must have at least 8 characters, including a number, a special character, and a mix of uppercase/lowercase."
            )
        return value


# Schema for User Login
class UserLogin(BaseModel):
    username: UsernameType
    password: PasswordType


# Response Schema for Authenticated User
class UserResponse(BaseModel):
    user_id: uuid.UUID
    username: str
    email: EmailStr
    is_verified: bool
    role: List[UserRole]

    class Config:
        from_attributes = True  # Enables ORM serialization


# Token Schema
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Token Data Schema (for extracting user info from JWT)
class TokenData(BaseModel):
    user_id: Optional[uuid.UUID] = None
    username: Optional[str] = None
    jti: Optional[str] = None
    expires_delta:Optional[datetime] = None
    role: List[UserRole]= []


# Password reset schema
class PasswordResetRequestModel(BaseModel):
    email: EmailStr


class PasswordResetConfirmModel(BaseModel):
    new_password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str = Field(..., min_length=8, max_length=100)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, value):
        if not re.match(PASSWORD_REGEX, value):
            raise ValueError(
                "Password must have at least 8 characters, including a number, a special character, and a mix of uppercase/lowercase."
            )
        return value
