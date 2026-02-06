from typing import Optional
from pydantic import BaseModel
from app.core.config import settings as env_settings
from app.services.settings_service import SettingsService
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)

class MonitoringConfig(BaseModel):
    prometheus_url: str
    loki_url: str
    grafana_url: str

class MonitoringConfigManager:
    _instance: Optional[MonitoringConfig] = None
    
    @classmethod
    def get_config(cls) -> MonitoringConfig:
        if cls._instance is None:
            # Fallback to env (with defaults from config.py) if not initialized
            return MonitoringConfig(
                prometheus_url=env_settings.PROMETHEUS_URL or "http://prometheus-k8s.monitoring:9090",
                loki_url=env_settings.LOKI_URL or "http://loki.monitoring:3100",
                grafana_url=env_settings.GRAFANA_URL or "http://grafana.monitoring:3000"
            )
        return cls._instance

    @classmethod
    async def reload_config(cls, db: AsyncSession):
        """Fetch settings from DB and merge with Env (DB priority)"""
        logger.info("Reloading Monitoring Config from DB...")
        try:
            db_settings = await SettingsService.get_all_settings(db)
            settings_map = {s.key: s.value for s in db_settings}
            
            # DB > Env > Default
            # Note: We must ensure we don't have None here, so provide fallbacks to defaults strings if Both DB and Env are missing/None
            prom = settings_map.get("prometheus_url") or env_settings.PROMETHEUS_URL or "http://prometheus-k8s.monitoring:9090"
            loki = settings_map.get("loki_url") or env_settings.LOKI_URL or "http://loki.monitoring:3100"
            grafana = settings_map.get("grafana_url") or env_settings.GRAFANA_URL or "http://grafana.monitoring:3000"
            
            cls._instance = MonitoringConfig(
                prometheus_url=prom,
                loki_url=loki,
                grafana_url=grafana
            )
            logger.info(f"Monitoring Config Reloaded.")
        except Exception as e:
            logger.error(f"Failed to reload Monitoring config: {e}")
