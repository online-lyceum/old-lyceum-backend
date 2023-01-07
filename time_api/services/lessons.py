import logging
import datetime as dt
from typing import Optional, Any

from sqlalchemy import select, exc
from fastapi import status, HTTPException

from .base import BaseService
from time_api.db import tables
from time_api.schemas.lessons import LessonCreate, Lesson
from time_api.schemas.lessons import DayLessonList
from time_api import schemas
from time_api.services.teachers import TeacherService

logger = logging.getLogger(__name__)


class LessonService(BaseService):

    async def get_list(
            self,
            class_id: Optional[int] = None,
            subgroup_id: Optional[int] = None,
            week: Optional[bool] = None,
            weekday: Optional[int] = None
    ) -> schemas.lessons.LessonList:
        lessons = await self._get_list(
                class_id=class_id,
                subgroup_id=subgroup_id,
                week=week,
                weekday=weekday
        )
        lessons = [await self._add_teacher(lesson) for lesson in lessons]
        return schemas.lessons.LessonList(
            lessons=lessons
        )

    async def _add_teacher(
            self,
            lesson: tables.Lesson
    ) -> dict[str, Any]:
        dct = schemas.lessons.InternalLesson.from_orm(lesson).dict()
        dct['teacher'] = await self._get_teacher(lesson.teacher_id)
        return dct

    async def _get_teacher(
            self,
            teacher_id: int
    ):
        teacher_service = TeacherService(self.session, self.response)
        return await teacher_service.get(teacher_id=teacher_id)

    async def _get_list(
            self,
            class_id: Optional[int] = None,
            subgroup_id: Optional[int] = None,
            week: Optional[bool] = None,
            weekday: Optional[int] = None
    ) -> list[tables.Class]:

        query = select(tables.Lesson)

        if subgroup_id is not None or class_id is not None:
            query = query.join(tables.LessonSubgroup)

        if subgroup_id is not None:
            query = query.filter_by(
                subgroup_id=subgroup_id
            )

        if class_id is not None:
            query = query.join(tables.Subgroup)
            query = query.filter_by(
                class_id=class_id
            )

        if week is not None:
            query = query.filter(
                tables.Lesson.week == week
            )

        if weekday is not None:
            query = query.filter(
                tables.Lesson.weekday == weekday
            )

        query = query.order_by(tables.Lesson.start_time)

        lessons = list(await self.session.scalars(query))
        if not lessons:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        return lessons

    async def get_weekday_list(
            self,
            weekday: Optional[int] = None,
            class_id: Optional[int] = None,
            subgroup_id: Optional[int] = None
    ) -> schemas.lessons.LessonList:
        lessons = await self._get_list(class_id=class_id,
                                       subgroup_id=subgroup_id,
                                       weekday=weekday)
        lessons = [await self._add_teacher(lesson) for lesson in lessons]
        logger.debug(f'Today has {lessons=}')
        returned_lessons: list[Lesson] = []
        for lesson in lessons:
            schemas_lesson = Lesson(
                name=lesson['name'],
                start_time=dt.time(**lesson['start_time']),
                end_time=dt.time(**lesson['end_time']),
                week=lesson['week'],
                weekday=lesson['weekday'],
                room=lesson['room'],
                school_id=lesson['school_id'],
                lesson_id=lesson['lesson_id'],
                teacher=schemas.teachers.Teacher(
                    **schemas.teachers.Teacher.from_orm(lesson['teacher']).dict()
                )
            )
            returned_lessons.append(schemas_lesson)

        return schemas.lessons.LessonList(
            lessons=returned_lessons
        )

    async def get_today_list(
            self,
            class_id: Optional[int] = None,
            subgroup_id: Optional[int] = None
    ) -> schemas.lessons.LessonList:
        today = dt.datetime.today().weekday()
        return await self.get_weekday_list(weekday=today,
                                           class_id=class_id,
                                           subgroup_id=subgroup_id)

    async def _today_is_done(self,
                             class_id: int,
                             subgroup_id: int) -> bool:
        try:
            lessons = await self.get_today_list(
                class_id=class_id,
                subgroup_id=subgroup_id
            )
            lessons_end_time = dt.time(**(lessons[-1]['end_time']))
            if lessons_end_time <= dt.datetime.now().time():
                return True

        except HTTPException(status_code=404):
            return True

        return False

    async def get_nearest_weekday_list(self,
                                       class_id: int,
                                       subgroup_id: int):
        if self._today_is_done(class_id=class_id,
                               subgroup_id=subgroup_id):
            return True

    async def get(
            self, *,
            lesson_schema: LessonCreate
    ) -> tables.Lesson:

        query = select(tables.Lesson).filter_by(
            name=lesson_schema.name,
            start_time=dt.time(**lesson_schema.start_time.dict()),
            end_time=dt.time(**lesson_schema.end_time.dict()),
            weekday=lesson_schema.weekday,
            school_id=lesson_schema.school_id,
            teacher_id=lesson_schema.teacher_id
        )
        lesson = await self.session.scalar(query)
        if lesson is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return lesson

    async def create(self, lesson_schema: LessonCreate):
        lesson_dct = lesson_schema.dict()
        lesson_dct['start_time'] = dt.time(**lesson_dct['start_time'])
        lesson_dct['end_time'] = dt.time(**lesson_dct['end_time'])
        try:
            new_lesson = tables.Lesson(**lesson_dct)
            self.session.add(new_lesson)
            await self.session.commit()
        except exc.IntegrityError:
            await self.session.rollback()
            new_lesson = await self.get(lesson_schema=lesson_schema)
            self.response.status_code = status.HTTP_200_OK
        return await self._add_teacher(new_lesson)

    async def add_subgroup_to_lesson(
            self,
            subgroup_lesson: schemas.subgroups_lessons.LessonSubgroupCreate
    ):
        try:
            new_lesson_subgroup = tables.LessonSubgroup(
                **subgroup_lesson.dict()
            )
            self.session.add(new_lesson_subgroup)
            await self.session.commit()
        except exc.IntegrityError:
            self.response.status_code = status.HTTP_200_OK
            return schemas.subgroups_lessons.LessonSubgroup(
                **subgroup_lesson.dict()
            )
        return new_lesson_subgroup
