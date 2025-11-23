from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from api.models.settings import AppSetting, AppSettingUpdate, CatalogIdSettings, CatalogIdPreview
from api.db.database import get_db
from api.db.models import AppSettingDB

router = APIRouter(prefix="/settings", tags=["settings"])

# Default settings
CATALOG_ID_FORMAT_KEY = "catalog_id_format"
CATALOG_ID_LAST_NUMBER_KEY = "catalog_id_last_number"
CATALOG_ID_LAST_YEAR_KEY = "catalog_id_last_year"

DEFAULT_CATALOG_ID_FORMAT = "{number}/{year}"


async def get_setting(db: AsyncSession, key: str, default: str | None = None) -> str | None:
    """Get a setting value by key."""
    result = await db.execute(select(AppSettingDB).where(AppSettingDB.key == key))
    setting = result.scalar_one_or_none()
    if setting:
        return setting.value
    return default


async def set_setting(db: AsyncSession, key: str, value: str) -> AppSettingDB:
    """Set a setting value, creating or updating as needed."""
    result = await db.execute(select(AppSettingDB).where(AppSettingDB.key == key))
    setting = result.scalar_one_or_none()

    if setting:
        setting.value = value
    else:
        setting = AppSettingDB(key=key, value=value)
        db.add(setting)

    await db.flush()
    await db.refresh(setting)
    return setting


@router.get("", response_model=List[AppSetting])
async def list_settings(db: AsyncSession = Depends(get_db)):
    """Get all application settings."""
    result = await db.execute(select(AppSettingDB))
    settings = result.scalars().all()
    return settings


@router.get("/{key}", response_model=AppSetting)
async def get_setting_by_key(key: str, db: AsyncSession = Depends(get_db)):
    """Get a specific setting by key."""
    result = await db.execute(select(AppSettingDB).where(AppSettingDB.key == key))
    setting = result.scalar_one_or_none()
    if not setting:
        raise HTTPException(status_code=404, detail=f"Setting '{key}' not found")
    return setting


@router.put("/{key}", response_model=AppSetting)
async def update_setting(key: str, data: AppSettingUpdate, db: AsyncSession = Depends(get_db)):
    """Update a setting value."""
    setting = await set_setting(db, key, data.value)
    await db.commit()
    return setting


@router.get("/catalog-id/config", response_model=CatalogIdSettings)
async def get_catalog_id_config(db: AsyncSession = Depends(get_db)):
    """Get catalog ID configuration."""
    format_value = await get_setting(db, CATALOG_ID_FORMAT_KEY, DEFAULT_CATALOG_ID_FORMAT)
    last_number = await get_setting(db, CATALOG_ID_LAST_NUMBER_KEY, "0")
    last_year = await get_setting(db, CATALOG_ID_LAST_YEAR_KEY, "0")

    return CatalogIdSettings(
        format=format_value or DEFAULT_CATALOG_ID_FORMAT,
        last_number=int(last_number or "0"),
        last_year=int(last_year or "0"),
    )


@router.put("/catalog-id/config", response_model=CatalogIdSettings)
async def update_catalog_id_config(data: CatalogIdSettings, db: AsyncSession = Depends(get_db)):
    """Update catalog ID configuration."""
    await set_setting(db, CATALOG_ID_FORMAT_KEY, data.format)
    await set_setting(db, CATALOG_ID_LAST_NUMBER_KEY, str(data.last_number))
    await set_setting(db, CATALOG_ID_LAST_YEAR_KEY, str(data.last_year))
    await db.commit()

    return data


@router.get("/catalog-id/preview", response_model=CatalogIdPreview)
async def preview_next_catalog_id(db: AsyncSession = Depends(get_db)):
    """Preview what the next catalog ID will be."""
    format_value = await get_setting(db, CATALOG_ID_FORMAT_KEY, DEFAULT_CATALOG_ID_FORMAT)
    last_number = int(await get_setting(db, CATALOG_ID_LAST_NUMBER_KEY, "0") or "0")
    last_year = int(await get_setting(db, CATALOG_ID_LAST_YEAR_KEY, "0") or "0")

    current_year = datetime.now().year % 100  # 2-digit year

    # Determine next number
    if last_year != current_year:
        next_number = 1
    else:
        next_number = last_number + 1

    # Generate preview
    next_id = (format_value or DEFAULT_CATALOG_ID_FORMAT).format(
        number=next_number,
        year=current_year,
    )

    return CatalogIdPreview(
        next_id=next_id,
        current_number=next_number,
        current_year=current_year,
    )


async def generate_catalog_id(db: AsyncSession) -> str:
    """Generate the next catalog ID using configured format.

    This function commits the counter update immediately to prevent
    duplicate IDs from being generated in concurrent requests.
    """
    format_value = await get_setting(db, CATALOG_ID_FORMAT_KEY, DEFAULT_CATALOG_ID_FORMAT)
    last_number = int(await get_setting(db, CATALOG_ID_LAST_NUMBER_KEY, "0") or "0")
    last_year = int(await get_setting(db, CATALOG_ID_LAST_YEAR_KEY, "0") or "0")

    current_year = datetime.now().year % 100  # 2-digit year

    # Reset to 1 if new year, otherwise increment
    if last_year != current_year:
        new_number = 1
    else:
        new_number = last_number + 1

    # Update settings and commit immediately to reserve this number
    await set_setting(db, CATALOG_ID_LAST_NUMBER_KEY, str(new_number))
    await set_setting(db, CATALOG_ID_LAST_YEAR_KEY, str(current_year))
    await db.commit()

    # Generate ID
    catalog_id = (format_value or DEFAULT_CATALOG_ID_FORMAT).format(
        number=new_number,
        year=current_year,
    )

    return catalog_id
