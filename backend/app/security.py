from datetime import datetime, timedelta, timezone
import hashlib
import hmac
from typing import Any, Dict

from jose import jwt

from .config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    calculated = get_password_hash(plain_password)
    return hmac.compare_digest(calculated, hashed_password)


def get_password_hash(password: str) -> str:
    salt = settings.password_salt.encode("utf-8")
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 390000).hex()


def create_access_token(subject: str, scopes: list[str] | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload: Dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "scope": " ".join(scopes or []),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
