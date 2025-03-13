from sqlmodel import SQLModel
from db.models import UserBase
from datetime import datetime
from typing import Optional
from uuid import UUID


class UserResponse(UserBase):
    user_id: UUID
    created_at: datetime


class UserUpdate(SQLModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None
    deleted_at: Optional[datetime] = None
