import os
import asyncio
import logging

import asyncpg


logger = logging.getLogger(__name__)


host = os.environ.get('POSTGRES_HOST') or '127.0.0.1'
db = os.environ.get('POSTGRES_DB') or 'db'
password = os.environ.get('POSTGRES_PASSWORD') or 'password'
user = os.environ.get('POSTGRES_USER') or 'postgres'
DATABASE_URL = f'postgresql+asyncpg://{user}:{password}@{host}/{db}'


async def connect_create_if_not_exists(user, database, password, host):
    try:
        conn = await asyncpg.connect(user=user, database=database,
                                     password=password, host=host)
        await conn.close()
    except asyncpg.InvalidCatalogNameError:
        # Database does not exist, create it.
        sys_conn = await asyncpg.connect(
            database='template1',
            user='postgres',
            password=password,
            host=host
        )
        await sys_conn.execute(
            f'CREATE DATABASE "{database}" OWNER "{user}"'
        )
        await sys_conn.close()


def run_init_db():
    asyncio.run(connect_create_if_not_exists(user, db, password, host))
    logger.info('DB initialization is done')
