"""Unit tests for health and authentication helpers."""

from httpx import AsyncClient
from jose import jwt

from api.config import settings
from api.routers.auth import create_access_token, get_password_hash, verify_password


async def test_healthcheck(client: AsyncClient) -> None:
    """Return the FastAPI integration health response."""
    response = await client.get("/api/python/healthcheck")

    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Integrated FastAPI Framework with Next.js successfully!",
    }


def test_password_hash_verification() -> None:
    """Accept the source password and reject a different password."""
    hashed_password = get_password_hash("correct horse battery staple")

    assert verify_password("correct horse battery staple", hashed_password)
    assert not verify_password("wrong password", hashed_password)


def test_access_token_contains_decodable_subject() -> None:
    """Encode a JWT subject that can be decoded with application settings."""
    token = create_access_token({"sub": "librarian"})

    payload = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
    )
    assert payload["sub"] == "librarian"
