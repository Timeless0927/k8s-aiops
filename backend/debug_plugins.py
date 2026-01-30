import asyncio
from app.db.session import AsyncSessionLocal
from app.services.plugin_store import PluginStoreService

async def main():
    async with AsyncSessionLocal() as session:
        print("Checking Plugin DB Status...")
        plugin = await PluginStoreService.get_plugin_state(session, "kubectl_plugin")
        if plugin:
            print(f"kubectl_plugin: {'ENABLED' if plugin.enabled else 'DISABLED'}")
        else:
            print("kubectl_plugin: NOT FOUND (Will default to disabled/new)")

if __name__ == "__main__":
    asyncio.run(main())
