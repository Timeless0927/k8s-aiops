from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.schemas.setting import SettingResponse, SettingUpdate
from app.services.settings_service import SettingsService

router = APIRouter()

@router.get("/", response_model=List[SettingResponse])
async def get_settings(db: AsyncSession = Depends(get_db)):
    """List all system settings."""
    return await SettingsService.get_all_settings(db)

@router.put("/{key}", response_model=SettingResponse)
async def update_setting(key: str, payload: SettingUpdate, db: AsyncSession = Depends(get_db)):
    """Update a specific setting."""
    return await SettingsService.set_setting(db, key, payload)
