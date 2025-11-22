from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum
from typing import Optional


class PatronStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"


class PatronBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    status: PatronStatus = PatronStatus.active
    borrowing_limit: int = 5
    notes: Optional[str] = None


class PatronCreate(PatronBase):
    pass


class PatronUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    status: Optional[PatronStatus] = None
    borrowing_limit: Optional[int] = None
    notes: Optional[str] = None


class Patron(PatronBase):
    id: str
    membership_id: str
    current_borrowed_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
