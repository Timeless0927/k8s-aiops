
import asyncio
from app.db.session import AsyncSessionLocal
from app.services.settings_service import SettingsService

async def check():
    async with AsyncSessionLocal() as session:
        setting = await SettingsService.get_setting(session, "openai_api_key")
        if setting and setting.value:
            print(f"Key in DB: {setting.value[:8]}... (Length: {len(setting.value)})")
        else:
            print("Key in DB: [EMPTY/NONE]")

if __name__ == "__main__":
    asyncio.run(check())
