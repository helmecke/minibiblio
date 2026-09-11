"""PostgreSQL-backed authentication API tests."""

from httpx import AsyncClient


async def register_user(
    client: AsyncClient,
    username: str = "admin",
    password: str = "correct-password",
):
    """Register a test user through the public endpoint."""
    return await client.post(
        "/api/python/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": password,
            "role": "admin",
        },
    )


async def test_first_registration_succeeds_and_later_registration_is_disabled(
    client: AsyncClient,
) -> None:
    """Permit only the first public registration."""
    first = await register_user(client)
    second = await register_user(client, username="second")

    assert first.status_code == 201
    assert first.json()["username"] == "admin"
    assert first.json()["is_active"] is True
    assert second.status_code == 403
    assert second.json()["detail"] == (
        "User registration is disabled. Contact administrator."
    )


async def test_login_and_authenticated_identity(client: AsyncClient) -> None:
    """Issue a token for valid credentials and resolve its user identity."""
    assert (await register_user(client)).status_code == 201

    login = await client.post(
        "/api/python/auth/login",
        json={"username": "admin", "password": "correct-password"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    identity = await client.get(
        "/api/python/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert identity.status_code == 200
    assert identity.json()["username"] == "admin"


async def test_login_rejects_incorrect_credentials(client: AsyncClient) -> None:
    """Reject an incorrect password without issuing a token."""
    assert (await register_user(client)).status_code == 201

    response = await client.post(
        "/api/python/auth/login",
        json={"username": "admin", "password": "incorrect-password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


async def test_identity_requires_valid_bearer_credentials(client: AsyncClient) -> None:
    """Reject missing and invalid access tokens."""
    missing = await client.get("/api/python/auth/me")
    invalid = await client.get(
        "/api/python/auth/me",
        headers={"Authorization": "Bearer not-a-valid-token"},
    )

    assert missing.status_code == 401
    assert invalid.status_code == 401
