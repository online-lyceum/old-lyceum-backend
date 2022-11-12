import asyncio
import logging
from typing import Optional
from argparse import ArgumentParser
import json

from aiohttp import web
import asyncpg


logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')
parser = ArgumentParser()
parser.add_argument('-w', '--web-host', default='0.0.0.0')
parser.add_argument('-p', '--web-port', default=80, type=int)
parser.add_argument('-H', '--postgres-host', default='0.0.0.0')
parser.add_argument('-U', '--user', default='postgres')
parser.add_argument('-D', '--database', default='db')
parser.add_argument('-P', '--postgres-port', default=5432, type=int)
parser.add_argument('-S', '--postgres-secret', required=False)

console_args = parser.parse_args()


class MyApplication(web.Application):
    def __init__(self, *args, **kwargs):
        super(MyApplication, self).__init__(*args, **kwargs)
        self.pool: Optional[asyncpg.Pool] = None


async def create_db_connection_pool(args, loop):
    return await asyncpg.create_pool(
        host=args.postgres_host,
        database=args.database,
        user=args.user,
        port=args.postgres_port,
        password=args.postgres_secret,
        loop=loop
    )


app = MyApplication()
routes = web.RouteTableDef()
loop = asyncio.new_event_loop()
app.pool = loop.run_until_complete(
    create_db_connection_pool(console_args, loop)
)


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


async def create_tables():
    async with app.pool.acquire() as conn:
        await conn.execute('''
                    CREATE TABLE IF NOT EXISTS School (
                        school_id SERIAL PRIMARY KEY UNIQUE,
                        name VARCHAR NOT NULL UNIQUE,
                        address VARCHAR
                    );
            ''')
        await conn.execute('''
                    CREATE TABLE IF NOT EXISTS Teacher (
                        teacher_id SERIAL PRIMARY KEY UNIQUE,
                        name VARCHAR
                    );
            ''')
        await conn.execute('''
                    CREATE TABLE IF NOT EXISTS LessonTime (
                        lesson_time_id SERIAL PRIMARY KEY UNIQUE,
                        school_id INT NOT NULL,
                        loop_day INT NOT NULL,
                        start_time TIME NOT NULL,
                        edit_time TIME NOT NULL,
                        CONSTRAINT fk_school_id
                            FOREIGN KEY (school_id)
                                REFERENCES School(school_id)
                    );
            ''')
        await conn.execute('''
                    CREATE TABLE IF NOT EXISTS Lesson (
                        lesson_id SERIAL PRIMARY KEY UNIQUE,
                        school_id INT NOT NULL,
                        teacher_id INT,
                        lesson_time_id INT NOT NULL,
                        CONSTRAINT fk_school_id
                            FOREIGN KEY (school_id)
                                REFERENCES School(school_id),
                        CONSTRAINT fk_teacher_id
                            FOREIGN KEY (teacher_id)
                                REFERENCES Teacher(teacher_id),
                        CONSTRAINT fk_lesson_time_id
                            FOREIGN KEY (lesson_time_id)
                                REFERENCES LessonTime(lesson_time_id)
                    );
            ''')
        await conn.execute('''
                    CREATE TABLE IF NOT EXISTS Class (
                        class_id SERIAL PRIMARY KEY UNIQUE,
                        number INT,
                        letter VARCHAR,
                        school_id INT NOT NULL,
                        teacher_id INT,
                        CONSTRAINT fk_teacher_id
                            FOREIGN KEY (teacher_id)
                                REFERENCES Teacher(teacher_id),
                        CONSTRAINT fk_school_id
                            FOREIGN KEY (school_id)
                                REFERENCES School(school_id)
                    );
            ''')
        await conn.execute('''
                CREATE TABLE IF NOT EXISTS Subgroup (
                    subgroup_id SERIAL PRIMARY KEY UNIQUE,
                    class_id INT,
                    CONSTRAINT fk_group_id
                        FOREIGN KEY (class_id)
                            REFERENCES Class(class_id)
                );
        ''')
        await conn.execute('''
                    CREATE TABLE IF NOT EXISTS GroupLesson (
                        group_id SERIAL PRIMARY KEY UNIQUE,
                        class_id INT,
                        CONSTRAINT fk_class_id
                            FOREIGN KEY (class_id)
                                REFERENCES Class(class_id)
                    );

            ''')


async def create_school(name, address):
    async with app.pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO School (name, address) VALUES
                ('{}', '{}')
            ON CONFLICT DO NOTHING;
        '''.format(name, address))


async def create_class(school_id, number, letter):
    async with app.pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO Class (school_id, number, letter) VALUES
                ('{}', '{}', '{}')
            ON CONFLICT DO NOTHING;
        '''.format(school_id, number, letter))


async def initialize_database(args):
    await create_db(args)
    await create_tables()
    await create_school('Лицей №2', 'Иркутск')
    await create_class(1, 10, 'Б')


loop.run_until_complete(initialize_database(console_args))


class JsonResponse(web.Response):
    def __init__(self, data):
        answer = json.dumps(
            data,
            ensure_ascii=False,
            indent=4
        )
        super(JsonResponse, self).__init__(
            text=answer,
            content_type='application/json'
        )


@routes.view('/')
class Root(web.View):
    async def get(self):
        return web.json_response('This is lyceum asynchronous API')


@routes.view('/school')
class School(web.View):
    async def get(self):
        async with app.pool.acquire() as connection:
            result = await connection.fetch("SELECT * FROM School")
        return JsonResponse({'schools': [dict(x) for x in result]})


@routes.view('/school/{school_id}/class')
class Class(web.View):
    async def get(self):
        school_id = self.request.match_info['school_id']
        async with app.pool.acquire() as connection:
            result = await connection.fetch('''
                    SELECT * FROM Class
                    WHERE class_id = '{}'
            '''.format(school_id))
        return JsonResponse({
            'school_id': school_id,
            'classes': [dict(x) for x in result]
        })


def run_app():
    app.add_routes(routes)
    web.run_app(
        app, host=console_args.web_host,
        port=console_args.web_port, loop=loop
    )


if __name__ == "__main__":
    run_app()
