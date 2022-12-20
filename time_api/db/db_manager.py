from datetime import time, datetime
import asyncio

import sqlalchemy.engine

from time_api import db
from time_api.db.base import init_models

from sqlalchemy.ext.asyncio import AsyncSession, AsyncResult
from sqlalchemy import select
from sqlalchemy import exc
import logging


logger = logging.getLogger(__name__)


async def get_school_list(session: AsyncSession):
    query = select(db.School)
    return await session.scalars(query)


async def get_cities(session: AsyncSession):
    query = select(db.Address.city).distinct()
    return await session.stream(query)


class LessonList:
    def __init__(self,
                 session: AsyncSession,
                 subgroup_id: int = None,
                 class_id: int = None):
        if subgroup_id is None and class_id is None:
            raise TypeError('One of subgroup_id and class_id must be '
                            'int, but None')
        self.class_id = class_id
        self.subgroup_id = subgroup_id
        self.session = session

    async def get_all_lessons(self):
        query = select(db.Lesson, db.Teacher)
        query = query.join(db.LessonSubgroup).join(db.Teacher).join(db.Subgroup)
        if self.subgroup_id is not None:
            query = query.filter(db.LessonSubgroup.subgroup_id == self.subgroup_id)
        else:
            query = query.join(db.Class)
            query = query.filter(db.Class.class_id == self.class_id)
        return await self.session.stream(query)

    async def get_current_or_next_day_with_lessons(self
        ) -> tuple[int, list[sqlalchemy.engine.Row]]:
        if await self._has_today_lessons():
            lessons = await self._get_day_lesson_and_teacher_rows(datetime.today().weekday())
            return (
                datetime.today().weekday(),
                lessons
            )
        else:
            for i in range(1, 8):
                weekday = (datetime.today().weekday() + i) % 7
                lessons = await self._get_day_lesson_and_teacher_rows(weekday)
                if lessons:
                    break
            else:
                return 0, []
            return weekday, lessons

    async def _get_day_lesson_steam(self, weekday: int, week: int = 0) -> AsyncResult:
        if week != 0:
            raise NotImplementedError("Double week support did not implemented")
        query = select(db.Lesson, db.Teacher)
        query = query.select_from(db.Lesson)
        query = query.join(db.LessonSubgroup)
        query = query.join(db.Teacher)
        if self.subgroup_id is not None:
            query = query.filter(db.LessonSubgroup.subgroup_id == self.subgroup_id)
        else:
            query = query.join(db.Subgroup)
            query = query.join(db.Class)
            query = query.filter(db.Class.class_id == self.class_id)
        query = query.filter(db.Lesson.weekday == weekday)
        query = query.filter(db.Lesson.week == week)
        return await self.session.stream(query)

    async def _get_day_lesson_and_teacher_rows(
            self,
            weekday: int,
            week: int = 0) -> list[sqlalchemy.engine.Row]:
        lesson_steam = await self._get_day_lesson_steam(weekday, week)
        return [lesson_and_teacher async for lesson_and_teacher in lesson_steam]

    async def _has_today_lessons(self):
        today = datetime.today()
        lessons = await self._get_day_lesson_and_teacher_rows(today.weekday())
        logger.debug(f'Today has {lessons=}')
        if not lessons:
            return False
        day_end_time = time(0, 0)
        for lesson, teacher in lessons:
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


async def create_lesson_and_get_teacher(session: AsyncSession, school_id: int,
                                        name: str, start_time: dict[str, int],
                                        end_time: dict[str, int], week: int,
                                        weekday: int, teacher_id: int):
    teacher_query = select(db.Teacher).filter_by(teacher_id=teacher_id)
    teacher = (await session.execute(teacher_query)).one()[0]
    query = select(db.Lesson).filter_by(name=name)
    query = query.filter_by(start_time=time(hour=start_time['hour'],
                                            minute=start_time['minute']))
    query = query.filter_by(end_time=time(hour=end_time['hour'],
                                          minute=end_time['minute']))
    query = query.filter_by(week=week)
    query = query.filter_by(weekday=weekday)
    query = query.filter_by(teacher_id=teacher_id)
    query = query.filter_by(school_id=school_id)

    try:
        return (await session.execute(query)).one()[0],teacher
    except exc.NoResultFound:
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
        return new_lesson, teacher


async def add_lesson_to_subgroup(session: AsyncSession, lesson_id: int,
                                 subgroup_id: int):
    query = select(db.LessonSubgroup).filter_by(subgroup_id=subgroup_id)
    query = query.filter_by(lesson_id=lesson_id)
    try:
        return (await session.execute(query)).one()[0]
    except exc.NoResultFound:
        new_lesson_subgroup = db.LessonSubgroup(lesson_id=lesson_id,
                                                subgroup_id=subgroup_id)
        session.add(new_lesson_subgroup)
        await session.commit()
        return new_lesson_subgroup


async def get_lessons_by_class_id(session: AsyncSession, class_id: int):
    query = select(db.Lesson, db.Teacher).join(db.LessonSubgroup)
    query = query.join(db.Subgroup).join(db.Class).join(db.Teacher)
    query = query.filter(db.Class.class_id == class_id)
    return await session.stream(query)


async def _delete_(session: AsyncSession, row):
    try:
        await session.delete(row.scalar_one())
    except exc.NoResultFound:
        return False
    await session.commit()
    return True


async def delete_subgroup_lesson(session: AsyncSession, subgroup_id: int, lesson_id: int):
    query = select(db.LessonSubgroup).filter_by(subgroup_id=subgroup_id)
    query = query.filter_by(lesson_id=lesson_id)
    row = await session.execute(query)
    return await _delete_(session, row)


async def delete_lesson(session: AsyncSession, lesson_id: int):
    query = select(db.Lesson).filter_by(lesson_id=lesson_id)
    row = await session.execute(query)
    return await _delete_(session, row)


async def delete_subgroup(session: AsyncSession, subgroup_id: int):
    query = select(db.Subgroup).filter_by(subgroup_id=subgroup_id)
    row = await session.execute(query)
    return await _delete_(session, row)


async def delete_class(session: AsyncSession, class_id: int):
    query = select(db.Class).filter_by(class_id=class_id)
    row = await session.execute(query)
    return await _delete_(session, row)


async def delete_school(session: AsyncSession, school_id: int):
    query = select(db.School).filter_by(school_id=school_id)
    row = await session.execute(query)
    return await _delete_(session, row)


async def _is_exist_(session: AsyncSession, query):
    is_exist: bool = True
    try:
        (await session.execute(query)).one()[0]
    except exc.NoResultFound:
        is_exist = False
    return is_exist


async def school_exist(session: AsyncSession, name: str,
                       city: str, place: str):
    query = select(db.Address).filter_by(city=city, place=place)
    return await _is_exist_(session, query)


async def class_exist(session: AsyncSession, school_id: int, number: int,
                      letter: str, class_type: str = "класс"):
    class_type_id = await _get_or_create_class_type_id(session, class_type)
    query = select(db.Class).filter_by(
        school_id=school_id, number=number,
        letter=letter, class_type_id=class_type_id
    )
    return await _is_exist_(session, query)


async def subgroup_exist(session: AsyncSession, class_id: int, name: str):
    query = select(db.Subgroup).filter_by(class_id=class_id, name=name)
    return await _is_exist_(session, query)


async def lesson_exist(session: AsyncSession, school_id: int,
                       name: str, start_time: dict[str, int],
                       end_time: dict[str, int], week: int,
                       weekday: int, teacher_id: int):
    query = select(db.Lesson).filter_by(name=name)
    query = query.filter_by(start_time=time(hour=start_time['hour'],
                                            minute=start_time['minute']))
    query = query.filter_by(end_time=time(hour=end_time['hour'],
                                          minute=end_time['minute']))
    query = query.filter_by(week=week)
    query = query.filter_by(weekday=weekday)
    query = query.filter_by(teacher_id=teacher_id)
    query = query.filter_by(school_id=school_id)
    return await _is_exist_(session, query)


async def subgroup_lesson_exist(session: AsyncSession, lesson_id: int,
                                subgroup_id: int):
    query = select(db.LessonSubgroup).filter_by(subgroup_id=subgroup_id)
    query = query.filter_by(lesson_id=lesson_id)
    return await _is_exist_(session, query)

async def get_subgroup_info(session: AsyncSession,
                            subgroup_id: int) -> sqlalchemy.engine.Row:
    query = select(
        db.Subgroup,
        db.Class,
        db.School
    )
    query = query.select_from(db.Subgroup).filter_by(subgroup_id=subgroup_id)
    query = query.join(db.Class).join(db.School)
    return (await session.execute(query)).one()
