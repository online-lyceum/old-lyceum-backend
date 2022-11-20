from async_lyceum_api.db.models import *
from async_lyceum_api.db.base import init_models

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import sqlalchemy


def run_init_models():
    asyncio.run(init_models())
    print("Done")


async def get_school_list(session: AsyncSession):
    return await session.stream(select(School))


async def add_school(session: AsyncSession, name: str, address: str):
    new_school = School(name=name, address=address)
    session.add(new_school)
    await session.commit()
    return new_school


async def get_classes(session: AsyncSession, school_id: int):
    query = select(Class.class_id, Class.number, Class.letter, ClassType.name)
    query = query.join(ClassType).join(School)
    query = query.filter(School.school_id == school_id)
    result = await session.stream(query)
    return result


async def _get_or_create_class_type_id(session: AsyncSession, class_type_name: str):
        query = select(ClassType.class_type_id)
        query = query.filter_by(name=class_type_name)
        result: sqlalchemy.engine.result.ChunkedIteratorResult = await session.execute(query)
        class_type_id_tuple = result.one_or_none()
        if class_type_id_tuple is None:
            class_type = ClassType(name=class_type_name)
            session.add(class_type)
            await session.commit()
            class_type_id = class_type.class_type_id
        else:
            class_type_id = class_type_id_tuple[0]
        return class_type_id


async def add_class(session: AsyncSession, school_id: int, number: int,
                    letter: str, class_type: str = "класс"):
    class_type_id = await _get_or_create_class_type_id(session, class_type)
    new_class = Class(school_id=school_id, number=number,
                      letter=letter, class_type_id=class_type_id)
    session.add(new_class)
    await session.commit()
    return new_class, class_type


async def create_subgroup(session: AsyncSession, class_id: int, name: str):
    new_subgroup = Subgroup(class_id=class_id, name=name)
    session.add(new_subgroup)
    await session.commit()
    return new_subgroup


async def get_subgroups(session: AsyncSession, class_id: int):
    query = select(Subgroup).filter_by(class_id=class_id)
    return await session.stream(query)


async def create_teacher(session: AsyncSession, name: str):
    new_teacher = Teacher(name=name)
    session.add(new_teacher)
    await session.commit()
    return new_teacher


async def get_teachers(session: AsyncSession):
    query = select(Teacher)
    return await session.stream(query)


async def initialize_database(args):
    await create_db(args)
    await create_tables()
    await create_school('Лицей №2', 'Иркутск')
    await create_school('Школа №35', 'Иркутск')
    await create_class(1, 10, 'Б'),
    await create_class(1, 10, 'В'),
    await create_teacher('Светлана Николаевна')
    await create_teacher('Мария Александровна')
    await create_lesson('Разговоры о важном', time(8, 0), time(8, 30), 0,
                        class_id=1, teacher_id=1)
    await create_lesson('Алгебра и начало анализа', time(8, 35), time(9, 5), 0,
                        class_id=1, teacher_id=2)
    await create_lesson('Разговоры о важном', time(8, 0), time(8, 30), 0,
                        class_id=2, teacher_id=2)
