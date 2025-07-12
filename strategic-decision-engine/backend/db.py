import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

POSTGRES_URL = os.getenv('POSTGRES_URL')
if not POSTGRES_URL:
    raise RuntimeError("POSTGRES_URL environment variable is not set.")

engine = create_async_engine(POSTGRES_URL, echo=True, future=True)
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session