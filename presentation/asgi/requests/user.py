import uuid
from datetime import datetime

from fastapi_users import schemas
from pydantic import BaseModel


class UserBase(BaseModel):
    name: str
    contact: str
    permissions: int
    membership_date: datetime


class UserRead(schemas.BaseUser[uuid.UUID], UserBase):
    pass


class UserCreate(schemas.BaseUserCreate, UserBase):
    pass


class UserUpdate(schemas.BaseUserUpdate, UserBase):
    pass
