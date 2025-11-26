from pydantic import BaseModel
from datetime import datetime, date
from enum import Enum
from typing import Optional


class PatronStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"


class PatronBase(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    birthdate: Optional[date] = None
    status: PatronStatus = PatronStatus.active


class PatronCreate(PatronBase):
    pass


class PatronUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    birthdate: Optional[date] = None
    status: Optional[PatronStatus] = None


class Patron(PatronBase):
    id: str
    membership_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
