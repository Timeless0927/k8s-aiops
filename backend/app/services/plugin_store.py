from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.plugin import PluginState

class PluginStoreService:
    @staticmethod
    async def get_plugin_state(session: AsyncSession, name: str) -> PluginState | None:
        result = await session.execute(select(PluginState).where(PluginState.name == name))
        return result.scalars().first()

    @staticmethod
    async def get_all_plugins(session: AsyncSession) -> list[PluginState]:
        result = await session.execute(select(PluginState))
        return result.scalars().all()

    @staticmethod
    async def set_plugin_enabled(session: AsyncSession, name: str, enabled: bool):
        # Update if exists, else insert (upsert logic or check first)
        plugin = await PluginStoreService.get_plugin_state(session, name)
        if plugin:
            plugin.enabled = enabled
        else:
            plugin = PluginState(name=name, enabled=enabled)
            session.add(plugin)
        await session.commit()
    
    @staticmethod
    async def update_plugin_config(session: AsyncSession, name: str, config: dict):
        plugin = await PluginStoreService.get_plugin_state(session, name)
        if plugin:
            plugin.config = config
        else:
            plugin = PluginState(name=name, enabled=False, config=config)
            session.add(plugin)
        await session.commit()

    @staticmethod
    async def ensure_plugin_exists(session: AsyncSession, name: str):
        """Ensure a plugin record exists in DB, default disabled if new."""
        plugin = await PluginStoreService.get_plugin_state(session, name)
        if not plugin:
            plugin = PluginState(name=name, enabled=False)
            session.add(plugin)
            await session.commit()
        return plugin
