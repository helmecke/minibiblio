"""PostgreSQL-backed fixtures for the FastAPI integration suite."""

import os
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from tests.database_guard import validate_test_database_url

try:
    TEST_DATABASE_URL = validate_test_database_url(os.getenv("TEST_DATABASE_URL"))
except RuntimeError as error:
    raise pytest.UsageError(str(error)) from error

# Application engines are created at import time, so configure the guarded URL first.
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from api.db.database import get_async_session, get_db
from api.index import app

APPLICATION_TABLES = (
    "loans",
    "catalog_items",
    "patrons",
    "users",
    "app_settings",
)


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def test_engine() -> AsyncIterator[AsyncEngine]:
    """Provide an engine for the migrated test database."""
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    async with engine.connect() as connection:
        database_name = await connection.scalar(text("SELECT current_database()"))
        assert database_name and "test" in database_name.lower()
    yield engine
    await engine.dispose()


async def truncate_application_tables(engine: AsyncEngine) -> None:
    """Remove committed test state from migrated application tables."""
    table_list = ", ".join(f'"{table}"' for table in APPLICATION_TABLES)
    async with engine.begin() as connection:
        await connection.execute(text(f"TRUNCATE TABLE {table_list} CASCADE"))


@pytest_asyncio.fixture(autouse=True)
async def clean_database(test_engine: AsyncEngine) -> AsyncIterator[None]:
    """Clean persisted state before and after every test."""
    await truncate_application_tables(test_engine)
    yield
    await truncate_application_tables(test_engine)


@pytest_asyncio.fixture
async def db_session(
    test_engine: AsyncEngine,
    clean_database: None,
) -> AsyncIterator[AsyncSession]:
    """Provide a per-test async database session."""
    session_factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    """Provide an ASGI client with both database dependencies overridden."""

    async def override_database() -> AsyncIterator[AsyncSession]:
        try:
            yield db_session
            await db_session.commit()
        except Exception:
            await db_session.rollback()
            raise

    app.dependency_overrides[get_db] = override_database
    app.dependency_overrides[get_async_session] = override_database
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(
            transport=transport, base_url="http://test"
        ) as http_client:
            yield http_client
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_async_session, None)
