import os
import asyncio

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import asyncpg


host = os.environ.get('POSTGRES_HOST') or '127.0.0.1'
db = os.environ.get('POSTGRES_DB') or 'db'
password = os.environ.get('POSTGRES_PASSWORD') or 'password'
user = os.environ.get('POSTGRES_USER') or 'postgres'
DATABASE_URL = f'postgresql+asyncpg://{user}:{password}@{host}/{db}'


async def connect_create_if_not_exists(user, database, password, host):
    try:
        conn = await asyncpg.connect(user=user, database=database,
                                     password=password, host=host)
    except asyncpg.InvalidCatalogNameError:
        # Database does not exist, create it.
        sys_conn = await asyncpg.connect(
            database='template1',
            user='postgres',
            password=password,
            host=host
        )
        await sys_conn.execute(
            text(f'CREATE DATABASE "{database}" OWNER "{user}"')
        )
        await sys_conn.close()

        # Connect to the newly created database.
        conn = await asyncpg.connect(user=user, database=database,
                                     password=password, host=host)

    return conn


asyncio.run(
    connect_create_if_not_exists(user, db, password, host)
)


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
