from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from app.models.setting import SystemSetting
from app.schemas.setting import SettingCreate, SettingUpdate

class SettingsService:
    @staticmethod
    async def get_setting(db: AsyncSession, key: str) -> Optional[SystemSetting]:
        result = await db.execute(select(SystemSetting).where(SystemSetting.key == key))
        return result.scalars().first()

    @staticmethod
    async def get_all_settings(db: AsyncSession):
        result = await db.execute(select(SystemSetting))
        return result.scalars().all()

    @staticmethod
    async def set_setting(db: AsyncSession, key: str, setting_in: SettingCreate | SettingUpdate):
        db_setting = await SettingsService.get_setting(db, key)
        if db_setting:
            db_setting.value = setting_in.value
            # Update desc/cat if provided? For simplicity, just value usually.
        else:
            if isinstance(setting_in, SettingUpdate):
                # Auto-create if not exists on update? Better restrict to Create.
                # But for UI ease, we often stick to a loose upsert.
                db_setting = SystemSetting(key=key, value=setting_in.value)
            else:
                db_setting = SystemSetting(
                    key=key, 
                    value=setting_in.value, 
                    category=setting_in.category,
                    description=setting_in.description
                )
            db.add(db_setting)
        
        await db.commit()
        await db.refresh(db_setting)
        return db_setting

    @staticmethod
    async def initialize_defaults(db: AsyncSession):
        """Seed default settings if missing."""
        defaults = [
            {"key": "dingtalk_webhook_url", "value": "", "category": "notification", "description": "Webhook URL for DingTalk notifications"},
            {"key": "dingtalk_secret", "value": "", "category": "notification", "description": "Security Secret (SEC...) for DingTalk Robot"},
            {"key": "enable_auto_fix", "value": "false", "category": "automation", "description": "Enable Agent to automatically execute fix commands"}
        ]
        
        for default in defaults:
             existing = await SettingsService.get_setting(db, default["key"])
             if not existing:
                 new_setting = SystemSetting(**default)
                 db.add(new_setting)
        await db.commit()
