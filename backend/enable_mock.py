import asyncio
from app.db.session import AsyncSessionLocal
from app.services.plugin_store import PluginStoreService

async def main():
    async with AsyncSessionLocal() as session:
        # 1. Enable mock_scenario
        await PluginStoreService.set_plugin_enabled(session, "mock_scenario", True)
        
        # 2. Disable real kubectl_plugin (Simulated override)
        # Actually PluginManager loads all, but we want mock to take precedence in ToolsRegistry?
        # NO, ToolsRegistry keys conflict. Last one wins.
        # So we must DISABLE kubectl_plugin to be safe, OR Mock must load AFTER.
        # Let's disable kubectl_plugin.
        await PluginStoreService.set_plugin_enabled(session, "kubectl_plugin", False)
        
        print("✅ Mock Scenario ENABLED. Real Kubectl DISABLED.")

if __name__ == "__main__":
    asyncio.run(main())
