from typing import Optional
from pydantic import BaseModel
from app.core.config import settings as env_settings
from app.services.settings_service import SettingsService
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)

class LLMConfig(BaseModel):
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model_name: Optional[str] = None

class LLMConfigManager:
    _instance: Optional[LLMConfig] = None
    
    @classmethod
    def get_config(cls) -> LLMConfig:
        if cls._instance is None:
            logger.info("LLMConfigManager: Instance is None, falling back to ENV.")
            # Fallback to env if not initialized
            return LLMConfig(
                api_key=env_settings.OPENAI_API_KEY,
                base_url=env_settings.OPENAI_BASE_URL,
                model_name=env_settings.MODEL_NAME
            )
        # logger.info(f"LLMConfigManager: Returning cached config. Key starts with: {cls._instance.api_key[:5] if cls._instance.api_key else 'None'}")
        return cls._instance

    @classmethod
    async def reload_config(cls, db: AsyncSession):
        """Fetch settings from DB and merge with Env (DB priority)"""
        logger.info("Reloading LLM Config from DB...")
        try:
            db_settings = await SettingsService.get_all_settings(db)
            settings_map = {s.key: s.value for s in db_settings}
            
            # DB > Env > Default
            api_key = settings_map.get("openai_api_key") or env_settings.OPENAI_API_KEY
            base_url = settings_map.get("openai_base_url") or env_settings.OPENAI_BASE_URL
            model_name = settings_map.get("openai_model_name") or env_settings.MODEL_NAME
            
            cls._instance = LLMConfig(
                api_key=api_key,
                base_url=base_url,
                model_name=model_name
            )
            logger.info(f"LLM Config Reloaded. Model: {model_name}, Key: {api_key[:10] if api_key else 'None'}...")
        except Exception as e:
            logger.error(f"Failed to reload LLM config: {e}")
