import os

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker


host = os.environ.get('POSTGRES_HOST') or '0.0.0.0'
db = os.environ.get('POSTGRES_DB') or 'db'
password = os.environ.get('POSTGRES_PASSWORD') or 'password'
user = os.environ.get('POSTGRES_USER') or 'postgres'
DATABASE_URL = f"postgresql+asyncpg://{user}:{password}@{host}/{db}"


engine = create_async_engine(DATABASE_URL)
Base = declarative_base()
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False,
    autocommit=False

)


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
