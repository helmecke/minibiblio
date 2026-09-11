"""Safety checks for destructive PostgreSQL test isolation."""

from sqlalchemy.engine import make_url


def validate_test_database_url(value: str | None) -> str:
    """Return a safe PostgreSQL test URL or raise before application imports."""
    if not value:
        raise RuntimeError("TEST_DATABASE_URL must be set")

    url = make_url(value)
    if not url.drivername.startswith("postgresql"):
        raise RuntimeError("TEST_DATABASE_URL must use PostgreSQL")
    if not url.database or "test" not in url.database.lower():
        raise RuntimeError("TEST_DATABASE_URL database name must contain 'test'")

    return value
