from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# SQLite URL (Async)
# Ensure settings.DATABASE_URL exists, fallback to local file
DATABASE_URL = getattr(settings, "DATABASE_URL", "sqlite+aiosqlite:///./app.db")

engine = create_async_engine(
    DATABASE_URL,
    echo=False, # Set to True for debug SQL logs
    future=True,
    pool_pre_ping=True
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
