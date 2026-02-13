import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.app.services.log_forensics import LogForensicsService
from backend.app.core.llm_config import LLMConfigManager
from backend.app.db.session import AsyncSessionLocal

async def test():
    print("Testing LogForensicsService...")
    
    # Initialize Config (mocking DB load or ensuring defaults)
    async with AsyncSessionLocal() as db:
        await LLMConfigManager.reload_config(db)
    
    config = LLMConfigManager.get_config()
    print(f"Config loaded. API Key present: {bool(config.api_key)}")
    print(f"Model: {config.model_name}")
    
    log_text = """
    2024-05-20 10:00:00 [error] nginx: [emerg] open() "/tmp/mime.types" failed (2: No such file or directory) in /tmp/nginx.conf:18
    2024-05-20 10:00:05 [warn] connection closed by peer
    """
    
    print(f"Analyzing log text ({len(log_text)} chars)...")
    try:
        result, viz = LogForensicsService.analyze_logs(log_text)
        print("Analysis Result:")
        print(result)
    except Exception as e:
        print(f"Analysis Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Fix for windows loop
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test())
