import logging
import datetime as dt
from typing import Optional

from sqlalchemy import select, exc
from fastapi import status, HTTPException

from .base import BaseService
from time_api.db import tables
from time_api.schemas.lessons import LessonCreate, Lesson, InternalLesson
from time_api.schemas.lessons import DayLessonList
from time_api.services.teachers import TeacherService


logger = logging.getLogger(__name__)


class LessonService(BaseService):
    async def get_list(
            self,
            class_id: Optional[int] = None,
            subgroup_id: Optional[int] = None,
            week: Optional[bool] = None,
            weekday: Optional[int] = None
    ) -> list[tables.Class]:

        query = select(tables.Lesson)
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
            query = query.filter_by(
                week=week
            )

        if weekday is not None:
            query = query.filter_by(
                weekday=weekday
            )

        lessons = list(await self.session.scalars(query))
        if not lessons:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return lessons

    async def get_today_list(
            self,
            class_id: Optional[int] = None,
            subgroup_id: Optional[int] = None
    ) -> DayLessonList:
        today = dt.datetime.today()
        lessons = await self.get_list(today.weekday())
        logger.debug(f'Today has {lessons=}')
        if not lessons:
            return False
        day_end_time = time(0, 0)
        for lesson, teacher in lessons:
            lesson_end_time = time(lesson.end_time.hour, lesson.end_time.minute)
            day_end_time = max(lesson_end_time, day_end_time)
        return day_end_time < datetime.now().time()

    async def get(
            self, *,
            lesson_schema: LessonCreate
    ):
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

    async def _format_to_schema(self, lesson: tables.Lesson):
        internal_lesson = InternalLesson.from_orm(lesson)
        logger.debug(f"{internal_lesson.dict()=}")
        teacher_service = TeacherService(self.session, self.response)
        teacher = await teacher_service.get(teacher_id=lesson.teacher_id)
        return Lesson(
            teacher=teacher,
            **internal_lesson.dict()
        )

    async def create(self, lesson_schema: LessonCreate):
        try:
            lesson_dct = lesson_schema.dict()
            lesson_dct['start_time'] = dt.time(**lesson_dct['start_time'])
            lesson_dct['end_time'] = dt.time(**lesson_dct['end_time'])
            new_lesson = tables.Lesson(**lesson_dct)
            self.session.add(new_lesson)
            await self.session.commit()
        except exc.IntegrityError:
            await self.session.rollback()
            new_lesson = await self.get(lesson_schema=lesson_schema)
        return await self._format_to_schema(new_lesson)
