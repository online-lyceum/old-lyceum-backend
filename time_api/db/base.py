import asyncio
import logging

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from .create import settings


logger = logging.getLogger(__name__)


DATABASE_URL = f'postgresql+asyncpg://' \
               f'{settings.postgres_user}:{settings.postgres_password}' \
               f'@{settings.postgres_host}/{settings.postgres_db}'


engine = create_async_engine(
    DATABASE_URL,
    pool_size=4,
    max_overflow=0,
    pool_reset_on_return=True
)
Base = declarative_base()
async_session = sessionmaker(
    engine, class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

from .tables import *


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    logger.info('Models initialisation is done')


def run_init_models():
    asyncio.run(init_models())
    print("Done")


async def get_session() -> AsyncSession:
    session: AsyncSession = async_session()
    try:
        yield session
    finally:
        await session.close()
