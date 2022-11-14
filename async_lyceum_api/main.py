import asyncio
import logging
from typing import Optional
from argparse import ArgumentParser
import json
from datetime import time

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
    await conn.execute('''
                DROP SCHEMA public CASCADE;
                CREATE SCHEMA public
            ''')


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
                        end_time TIME NOT NULL,
                        CONSTRAINT fk_school_id
                            FOREIGN KEY (school_id)
                                REFERENCES School(school_id)
                    );
            ''')
        await conn.execute('''
                    CREATE TABLE IF NOT EXISTS Lesson (
                        lesson_id SERIAL PRIMARY KEY UNIQUE,
                        school_id INT NOT NULL,
                        name VARCHAR NOT NULL,
                        teacher_id INT NOT NULL,
                        lesson_time_id INT NOT NULL,
                        CONSTRAINT fk_school_id
                            FOREIGN KEY (school_id)
                                REFERENCES School(school_id),
                        CONSTRAINT fk_teacher_id
                            FOREIGN KEY (teacher_id)
                                REFERENCES Teacher(teacher_id),
                        CONSTRAINT fk_lesson_time_id
                            FOREIGN KEY (lesson_time_id)
                                REFERENCES LessonTime(lesson_time_id),
                        CONSTRAINT uq_lesson
                            UNIQUE (school_id, name, lesson_time_id, teacher_id)
                    );
            ''')
        await conn.execute('''
                    CREATE TABLE IF NOT EXISTS Class (
                        class_id SERIAL PRIMARY KEY UNIQUE,
                        number INT NOT NULL,
                        letter VARCHAR,
                        school_id INT NOT NULL,
                        teacher_id INT,
                        CONSTRAINT fk_teacher_id
                            FOREIGN KEY (teacher_id)
                                REFERENCES Teacher(teacher_id),
                        CONSTRAINT fk_school_id
                            FOREIGN KEY (school_id)
                                REFERENCES School(school_id),
                        CONSTRAINT uq_class
                        UNIQUE (number, letter, school_id)
                    );
            ''')
        await conn.execute('''
                CREATE TABLE IF NOT EXISTS Subgroup (
                    subgroup_id SERIAL PRIMARY KEY UNIQUE,
                    class_id INT NOT NULL,
                    name VARCHAR,
                    CONSTRAINT fk_group_id
                        FOREIGN KEY (class_id)
                            REFERENCES Class(class_id),
                    CONSTRAINT uq_class_id_name
                        UNIQUE (class_id, name)
                );
        ''')
        await conn.execute('''
                CREATE TABLE IF NOT EXISTS SubgroupLesson (
                    subgroup_lesson_id SERIAL PRIMARY KEY UNIQUE,
                    subgroup_id INT NOT NULL,
                    lesson_id INT NOT NULL,
                    CONSTRAINT fk_subgroup_id
                        FOREIGN KEY (subgroup_id)
                            REFERENCES Subgroup(subgroup_id),
                    CONSTRAINT fk_lesson_id
                        FOREIGN KEY (lesson_id)
                            REFERENCES Lesson(lesson_id),
                    CONSTRAINT uq_lesson_id_subgroup_id
                        UNIQUE (subgroup_id, lesson_id)
                );
        ''')


async def create_school(name, address):
    async with app.pool.acquire() as conn:
        await conn.execute(f'''
            INSERT INTO School (name, address) VALUES
                ('{name}', '{address}')
            ON CONFLICT DO NOTHING;
        ''')


async def create_teacher(name):
    async with app.pool.acquire() as conn:
        await conn.execute(f'''
            INSERT INTO Teacher (name) VALUES
                ('{name}')
            ON CONFLICT DO NOTHING;
        ''')


async def create_class(school_id, number, letter):
    async with app.pool.acquire() as conn:
        await conn.execute(f'''
            INSERT INTO Class (school_id, number, letter) VALUES
                ('{school_id}', '{number}', '{letter}')
            ON CONFLICT DO NOTHING;
        ''')
        res = await conn.fetchrow(f'''
            SELECT class_id FROM Class
                WHERE school_id = '{school_id}' AND
                      number = '{number}' AND
                      letter = '{letter}'
        ''')
        await conn.execute(f'''
            INSERT INTO Subgroup (class_id, name) VALUES
                ('{res['class_id']}', 'default')
            ON CONFLICT DO NOTHING;
        ''')


async def create_lesson(name, start_time, end_time, loop_day, *,
                        class_id=None, subgroup_id=None, teacher_id=None):
    if class_id is None and subgroup_id is None:
        raise TypeError('Set class_id or subgroup_id')
    async with app.pool.acquire() as conn:
        conn: asyncpg.Connection
        if class_id is not None:
            school_id_row = await conn.fetchrow(f'''
                    SELECT school_id 
                        FROM Class
                    WHERE class_id = '{class_id}'
            ''')
        if subgroup_id is not None:
            school_id_row = await conn.fetchrow(f'''
                    SELECT school_id 
                        FROM Class
                    JOIN Subgroup ON Class.class_id = Subgroup_id.class_id
                    WHERE Subgroup.subgroup_id = '{subgroup_id}'
            ''')
        school_id = school_id_row['school_id']
        await conn.execute(f'''
                INSERT INTO LessonTime (
                            school_id, 
                            start_time, 
                            end_time,
                            loop_day
                        ) VALUES
                    ('{school_id}', '{start_time}', '{end_time}', '{loop_day}')
                ON CONFLICT DO NOTHING;
        ''')
        lesson_time_id_row = await conn.fetchrow(f'''
                SELECT lesson_time_id 
                    FROM LessonTime
                WHERE start_time = '{start_time}' AND 
                      end_time = '{end_time}'
        ''')
        lesson_time_id = lesson_time_id_row['lesson_time_id']
        await conn.execute(f'''
                INSERT INTO Lesson (school_id, name, lesson_time_id, teacher_id) VALUES
                    ('{school_id}', '{name}', '{lesson_time_id}', '{teacher_id}')
                ON CONFLICT DO NOTHING;
        ''')
        lesson_id_row = await conn.fetchrow(f'''
                SELECT lesson_id FROM Lesson
                    WHERE name = '{name}' AND 
                          lesson_time_id = '{lesson_time_id}'
        ''')
        lesson_id = lesson_id_row['lesson_id']
        if subgroup_id is not None:
            await conn.execute(f'''
                    INSERT INTO SubgroupLesson (
                                    lesson_id,
                                    subgroup_id
                                    ) VALUES
                        ('{lesson_id}', '{subgroup_id}')
                    ON CONFLICT DO NOTHING
            ''')
        elif class_id is not None:
            subgroups = await conn.fetch(f'''
                    SELECT subgroup_id FROM Subgroup
                        WHERE class_id = '{class_id}' 
            ''')
            await conn.execute(f'''
                    INSERT INTO SubgroupLesson (
                                    lesson_id, 
                                    subgroup_id
                                    ) VALUES
                        {', '.join([f"('{lesson_id}', "
                                    f"'{subgroup_row['subgroup_id']}')" 
                                    for subgroup_row in subgroups])}
                    ON CONFLICT DO NOTHING;
            ''')


async def initialize_database(args):
    await create_db(args)
    await create_tables()
    await create_school('Лицей №2', 'Иркутск')
    await create_class(1, 10, 'Б'),
    await create_teacher('Светлана Николаевна')
    await create_lesson('Разговоры о важном', time(8, 0), time(8, 30), 0,
                        class_id=1, teacher_id=1)


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


@routes.view('/school/{school_id}/lesson')
class Lesson(web.View):
    async def get(self):
        school_id = self.request.match_info['school_id']
        async with app.pool.acquire() as connection:
            result = await connection.fetch('''
                    SELECT
                            Lesson.name,
                            LessonTime.loop_day, 
                            LessonTime.start_time,
                            LessonTime.end_time
                        FROM Lesson
                    JOIN Teacher
                        ON Lesson.teacher_id = Teacher.teacher_id
                    JOIN SubgroupLesson 
                        ON Lesson.lesson_id = SubgroupLesson.lesson_id
                    JOIN Subgroup
                        ON SubgroupLesson.subgroup_id = Subgroup.subgroup_id
                    JOIN Class
                        ON Subgroup.class_id = Class.class_id
                    JOIN LessonTime
                        ON Lesson.lesson_time_id = LessonTime.lesson_time_id 
                            AND Class.school_id = LessonTime.school_id
                    WHERE Class.school_id = '{}'
            '''.format(school_id))
        return JsonResponse({
            'school_id': school_id,
            'lessons': [
                {
                    'name': x['name'],
                    'loop_day': x['loop_day'],
                    'start_time': [x['start_time'].hour,
                                   x['start_time'].minute],
                    'end_time': [x['end_time'].hour,
                                 x['end_time'].minute]
                } for x in result]
        })


@routes.view('/class/{class_id}/lesson')
class LessonsOfClass(web.View):
    async def get(self):
        class_id = self.request.match_info['class_id']
        async with app.pool.acquire() as conn:
            result = await conn.fetch(f'''
                    SELECT 
                            Lesson.name AS lesson_name,
                            LessonTime.loop_day, 
                            LessonTime.start_time,
                            LessonTime.end_time,
                            Teacher.name AS teacher_name
                        FROM Lesson
                    JOIN Teacher
                        ON Lesson.teacher_id = Teacher.teacher_id
                    JOIN SubgroupLesson
                        ON Lesson.lesson_id = SubgroupLesson.lesson_id
                    JOIN Subgroup
                        ON SubgroupLesson.subgroup_id = Subgroup.subgroup_id
                    JOIN Class
                        ON Subgroup.class_id = Class.class_id
                    JOIN LessonTime
                        ON Lesson.lesson_time_id = LessonTime.lesson_time_id 
                            AND Class.school_id = LessonTime.school_id
                    WHERE Class.class_id = '{class_id}'
            ''')
            return JsonResponse({
                'class_id': class_id,
                'lessons':
                    [
                        {
                            'name': x['lesson_name'],
                            'loop_day': x['loop_day'],
                            'start_time': [x['start_time'].hour,
                                           x['start_time'].minute],
                            'end_time': [x['end_time'].hour,
                                         x['end_time'].minute],
                            'teacher': x['teacher_name']
                        } for x in result
                    ]
            })


def run_app():
    app.add_routes(routes)
    web.run_app(
        app, host=console_args.web_host,
        port=console_args.web_port, loop=loop
    )


if __name__ == "__main__":
    run_app()
