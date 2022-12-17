import logging
from typing import Optional
import datetime as dt

from sqlalchemy import select, exc
from fastapi import status, HTTPException

from .base import BaseService
from time_api.db import tables
from time_api.schemas.lessons import LessonCreate


logger = logging.getLogger(__name__)


class LessonService(BaseService):
    async def get_list(
            self,
            class_id: Optional[int] = None,
            subgroup_id: Optional[int] = None
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

        lessons = list(await self.session.scalars(query))
        if not lessons:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return lessons

    async def get(
            self, *,
            lesson_schema: LessonCreate
    ):
        query = select(tables.Lesson).filter_by(
            name=lesson_schema.name,
            start_time=lesson_schema.start_time,
            end_time=lesson_schema.end_time,
            weekday=lesson_schema.weekday,
            school_id=lesson_schema.school_id,
            teacher_id=lesson_schema.teacher_id
        )
        class_ = await self.session.scalar(query)
        if class_ is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return class_

    async def create(self, lesson_schema: LessonCreate):
        try:
            lesson_dct = lesson_schema.dict()
            lesson_dct['start_time'] = dt.time(
                hour=lesson_schema.start_time.hour,
                minute=lesson_schema.start_time.minute,
                second=1
            )
            lesson_dct['end_time'] = dt.time(
                hour=lesson_schema.end_time.hour,
                minute=lesson_schema.end_time.minute,
                second=1
            )
            new_lesson = tables.Lesson(**lesson_dct)
            self.session.add(new_lesson)
            await self.session.commit()
        except exc.IntegrityError:
            await self.session.rollback()
            new_lesson = await self.get(lesson_schema=lesson_schema)
        return new_lesson
