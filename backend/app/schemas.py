from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    scope: str | None = None
    issued_at: datetime = Field(default_factory=datetime.utcnow)


class LoginRequest(BaseModel):
    username: str
    password: str


class User(BaseModel):
    username: str
    is_admin: bool = False


class AuthenticatedUser(User):
    scopes: list[str] = Field(default_factory=list)


class LoginResponse(BaseModel):
    token: Token
    user: AuthenticatedUser
