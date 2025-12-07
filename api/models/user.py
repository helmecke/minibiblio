from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from api.db.models import UserRole


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr | None = None
    role: UserRole = UserRole.user


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    role: UserRole | None = None
    is_active: bool | None = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


class UserResponse(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str | None = None


class LoginRequest(BaseModel):
    username: str
    password: str
