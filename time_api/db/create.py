import asyncio
from loguru import logger

import asyncpg
from pydantic import BaseSettings


class Settings(BaseSettings):
    postgres_host = '127.0.0.1'
    postgres_db = 'db'
    postgres_password = 'password'
    postgres_user = 'postgres'


settings = Settings()


async def connect_create_if_not_exists(user, database, password, host):
    success = False
    for i in range(5):
        try:
            conn = await asyncpg.connect(user=user, database=database,
                                         password=password, host=host)
            await conn.close()
            success = True
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
            success = True
        except ConnectionResetError:
            logger.info("Connect error retry in 5 seconds...")
            await asyncio.sleep(5)
        if success:
            break
    if success:
        logger.info('DB initialization is done')
    else:
        logger.info('DB initialization ERROR')


def run_init_db():
    asyncio.run(connect_create_if_not_exists(
        settings.postgres_user,
        settings.postgres_db,
        settings.postgres_password,
        settings.postgres_host))
