
import asyncio
from app.db.session import AsyncSessionLocal
from app.services.settings_service import SettingsService

async def check():
    async with AsyncSessionLocal() as session:
        settings = await SettingsService.get_all_settings(session)
        print("--- Current DB Settings ---")
        for s in settings:
            if "openai" in s.key:
                val = s.value
                if "api_key" in s.key and val:
                    val = val[:8] + "..." + val[-4:]
                print(f"{s.key}: {val}")

if __name__ == "__main__":
    asyncio.run(check())
