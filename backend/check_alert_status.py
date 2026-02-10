import asyncio
import os
import sys

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import AsyncSessionLocal
from app.db.models.alert import Alert
from sqlalchemy import select

async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Alert))
        alerts = result.scalars().all()
        print(f"Total Alerts: {len(alerts)}")
        for i, a in enumerate(alerts):
            print(f"[{i}] ID: {a.id}, Title: {a.title}, Status: {a.status}, Created: {a.created_at}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
