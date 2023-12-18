import uuid
from datetime import datetime

from pydantic.main import BaseModel


class User(BaseModel):
    id: uuid.UUID
    email: str
    hashed_password: str
    is_active: bool
    is_superuser: bool
    is_verified: bool

    name: str
    contact: str
    permissions: int
    membership_date: datetime
