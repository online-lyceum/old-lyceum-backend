from datetime import time, datetime
import asyncio

from async_lyceum_api import db
from async_lyceum_api.db import my_exc
from async_lyceum_api.db.base import init_models

from sqlalchemy.ext.asyncio import AsyncSession, AsyncResult
from sqlalchemy import select
from sqlalchemy import exc


def run_init_models():
    asyncio.run(init_models())
    print("Done")


async def get_school_list(session: AsyncSession):
    query = select(db.School.school_id, db.School.name,
                   db.Address.city, db.Address.place)
    query = query.select_from(db.School)
    query = query.join(db.Address)

    return await session.stream(query)


async def get_cities(session: AsyncSession):
    query = select(db.Address.city).distinct()
    return await session.stream(query)



class SubgroupLessonList:
    def __init__(self, session: AsyncSession, subgroup_id: int):
        self.subgroup_id = subgroup_id
        self.session = session

    async def get_all_lessons(self):
        query = select(db.Lesson).join(db.LessonSubgroup)
        query = query.filter_by(subgroup_id=self.subgroup_id)
        return await self.session.stream(query)

    async def get_current_or_next_day_with_lessons(self) -> tuple[int, list]:
        if await self._has_today_lessons():
            lessons_stream = await self._get_day_lessons(datetime.today().weekday())
            return (
                datetime.today().weekday(),
                [x async for x in lessons_stream]
            )
        else:
            for i in range(1, 7):
                weekday = (datetime.today().weekday() + i) % 7
                lessons_steam = await self._get_day_lessons(weekday)
                lessons = [x async for x in lessons_steam]
                if lessons:
                    break
            else:
                raise my_exc.LessonsNotFound(subgroup_id=self.subgroup_id)
            return weekday, lessons

    async def _get_day_lessons(self, weekday: int, week: int = 0) -> AsyncResult:
        if week != 0:
            raise NotImplementedError("Double week support did not implemented")
        query = select(db.Lesson)
        query = query.select_from(db.Lesson)
        query = query.join(db.LessonSubgroup)
        query = query.filter(db.Subgroup.subgroup_id == self.subgroup_id)
        query = query.filter(db.Lesson.weekday == weekday)
        query = query.filter(db.Lesson.week == week)
        return await self.session.stream(query)

    async def _has_today_lessons(self):
        today = datetime.today()
        lessons = await self._get_day_lessons(today.weekday())
        if not lessons:
            return False
        day_end_time = time(0, 0)
        async for lesson in lessons:
            lesson_end_time = time(lesson.end_time.hour, lesson.end_time.minute)
            day_end_time = max(lesson_end_time, day_end_time)
        return day_end_time < datetime.now().time()


async def add_school_with_address(session: AsyncSession, name: str,
                                  city: str, place: str):
    query = select(db.Address).filter_by(city=city, place=place)
    try:
        address = (await session.execute(query)).one()[0]
    except exc.NoResultFound:
        new_address = db.Address(city=city, place=place)
        session.add(new_address)
        await session.flush([new_address])
        address = new_address

    query = select(db.School).filter_by(name=name,
                                        address_id=address.address_id)
    try:
        return (await session.execute(query)).one()[0], address
    except exc.NoResultFound:
        new_school = db.School(name=name, address_id=address.address_id)
        session.add(new_school)
        await session.commit()
        return new_school, address


async def get_classes(session: AsyncSession, school_id: int):
    query = select(db.Class.class_id, db.Class.number, db.Class.letter,
                   db.ClassType.name)
    query = query.join(db.ClassType).join(db.School)
    query = query.filter(db.School.school_id == school_id)
    result = await session.stream(query)
    return result


async def _get_or_create_class_type_id(session: AsyncSession,
                                       class_type_name: str):
    query = select(db.ClassType.class_type_id)
    query = query.filter_by(name=class_type_name)
    result = await session.execute(
        query)
    class_type_id_tuple = result.one_or_none()
    if class_type_id_tuple is None:
        class_type = db.ClassType(name=class_type_name)
        session.add(class_type)
        await session.commit()
        class_type_id = class_type.class_type_id
    else:
        class_type_id = class_type_id_tuple[0]
    return class_type_id


async def add_class(session: AsyncSession, school_id: int, number: int,
                    letter: str, class_type: str = "класс"):
    class_type_id = await _get_or_create_class_type_id(session, class_type)
    query = select(db.Class).filter_by(
            school_id=school_id, number=number,
            letter=letter, class_type_id=class_type_id
        )
    try:
        return (await session.execute(query)).one()[0], class_type
    except exc.NoResultFound:
        new_class = db.Class(school_id=school_id, number=number,
                             letter=letter, class_type_id=class_type_id)
        session.add(new_class)
        await session.commit()
        return new_class, class_type


async def create_subgroup(session: AsyncSession, class_id: int, name: str):
    query = select(db.Subgroup).filter_by(class_id=class_id, name=name)
    try:
        return (await session.execute(query)).one()[0]
    except exc.NoResultFound:
        new_subgroup = db.Subgroup(class_id=class_id, name=name)
        session.add(new_subgroup)
        await session.commit()
        return new_subgroup


async def get_subgroups(session: AsyncSession, class_id: int):
    query = select(db.Subgroup).filter_by(class_id=class_id)
    return await session.stream(query)


async def create_teacher(session: AsyncSession, name: str):
    new_teacher = db.Teacher(name=name)
    session.add(new_teacher)
    await session.commit()
    return new_teacher


async def get_teachers(session: AsyncSession):
    query = select(db.Teacher)
    return await session.stream(query)


async def create_lesson(session: AsyncSession, school_id: int,
                        name: str, start_time: dict[str, int],
                        end_time: dict[str, int], week: int,
                        weekday: int, teacher_id: int):
    new_lesson = db.Lesson(
        name=name,
        start_time=time(hour=start_time['hour'],
                        minute=start_time['minute']),
        end_time=time(hour=end_time['hour'],
                      minute=end_time['minute']),
        week=week,
        weekday=weekday,
        teacher_id=teacher_id,
        school_id=school_id
    )
    session.add(new_lesson)
    await session.commit()
    return new_lesson


async def add_lesson_to_subgroup(session: AsyncSession, lesson_id: int,
                                 subgroup_id: int):
    new_lesson_subgroup = db.LessonSubgroup(lesson_id=lesson_id,
                                            subgroup_id=subgroup_id)
    session.add(new_lesson_subgroup)
    await session.commit()
    return new_lesson_subgroup


async def get_lessons_by_class_id(session: AsyncSession, class_id: int):
    query = select(db.Lesson).join(db.LessonSubgroup)
    query = query.join(db.Subgroup).join(db.Class)
    query = query.filter(db.Class.class_id == class_id)
    return await session.stream(query)


async def delete_subgroup(session: AsyncSession, subgroup_id: int):
    query = select(db.Subgroup).filter_by(subgroup_id=subgroup_id)
    row = await session.execute(query)
    await session.delete(row.scalar_one())
    await session.commit()


async def delete_class(session: AsyncSession, class_id: int):
    query = select(db.Class).filter_by(class_id=class_id)
    row = await session.execute(query)
    await session.delete(row.scalar_one())
    await session.commit()


async def delete_school(session: AsyncSession, school_id: int):
    query = select(db.School).filter_by(school_id=school_id)
    row = await session.execute(query)
    await session.delete(row.scalar_one())
    await session.commit()
