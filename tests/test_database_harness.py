"""Integration tests for migrations and fixture isolation."""

from sqlalchemy import inspect, select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from api.db.models import AppSettingDB


async def test_migrations_created_application_tables(test_engine: AsyncEngine) -> None:
    """Query tables produced exclusively by the Alembic chain."""
    async with test_engine.connect() as connection:
        table_names = await connection.run_sync(
            lambda sync_connection: inspect(sync_connection).get_table_names()
        )

    assert {
        "alembic_version",
        "app_settings",
        "catalog_items",
        "loans",
        "patrons",
        "users",
    }.issubset(table_names)


async def test_committed_record_is_visible_within_test(
    db_session: AsyncSession,
) -> None:
    """Commit state through the fixture for the following isolation check."""
    db_session.add(AppSettingDB(key="isolation-check", value="present"))
    await db_session.commit()
    result = await db_session.scalar(
        select(AppSettingDB).where(AppSettingDB.key == "isolation-check")
    )
    assert result is not None


async def test_committed_record_is_absent_from_next_test(
    db_session: AsyncSession,
) -> None:
    """Observe that fixture cleanup removed the previous test's commit."""
    result = await db_session.scalar(
        select(AppSettingDB).where(AppSettingDB.key == "isolation-check")
    )
    assert result is None
