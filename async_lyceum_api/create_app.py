import asyncio
from typing import Optional
import logging

from aiohttp import web
import asyncpg

from async_lyceum_api import console_args


logger = logging.getLogger(__name__)


class MyApplication(web.Application):
    def __init__(self, *args, **kwargs):
        super(MyApplication, self).__init__(*args, **kwargs)
        self.pool: Optional[asyncpg.Pool] = None


async def create_db_connection_pool(args, application_loop):
    return await asyncpg.create_pool(
        host=args.postgres_host,
        database=args.database,
        user=args.user,
        port=args.postgres_port,
        password=args.postgres_secret,
        loop=application_loop
    )


def create_app_routes_loop():
    app = MyApplication(logger=logger)
    routes = web.RouteTableDef()
    loop = asyncio.new_event_loop()
    app.pool = loop.run_until_complete(
        create_db_connection_pool(console_args, loop)
    )

    return app, routes, loop


async def create_db(args):
    conn = await asyncpg.connect(
        host=args.postgres_host,
        port=args.postgres_port,
        user=args.user,
        password=args.postgres_secret
    )
    try:
        await conn.execute(f"CREATE DATABASE {args.database}")
    except asyncpg.exceptions.DuplicateDatabaseError:
        pass
    await conn.execute('''
                DROP SCHEMA public CASCADE;
                CREATE SCHEMA public;
            ''')
