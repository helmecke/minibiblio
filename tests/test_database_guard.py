"""Tests for the destructive-cleanup database guard."""

import pytest

from tests.database_guard import validate_test_database_url


def test_requires_explicit_database_url() -> None:
    """Reject an absent test database URL."""
    with pytest.raises(RuntimeError, match="must be set"):
        validate_test_database_url(None)


@pytest.mark.parametrize(
    "url",
    [
        "sqlite+aiosqlite:///test.db",
        "postgresql+asyncpg://postgres:password@localhost:5432/minibiblio",
    ],
)
def test_rejects_unsafe_database_urls(url: str) -> None:
    """Reject non-PostgreSQL and non-test database URLs."""
    with pytest.raises(RuntimeError):
        validate_test_database_url(url)


def test_accepts_explicit_postgresql_test_database() -> None:
    """Accept a PostgreSQL URL whose database is test-designated."""
    url = "postgresql+asyncpg://postgres:password@localhost:5432/testdatabase"
    assert validate_test_database_url(url) == url
