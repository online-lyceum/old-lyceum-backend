import logging
import datetime as dt
from typing import Optional, Any
from itertools import groupby

from sqlalchemy import select, exc
from fastapi import status, HTTPException

from time_api.services.base import BaseService
from time_api.db import tables
from time_api.schemas.lessons import LessonCreate, Lesson
from time_api import schemas

logger = logging.getLogger(__name__)


class LessonHotfixService(BaseService):
    async def create(self, hotfix_schema: schemas.lessons.LessonHotfix):
        hotfix_schema = hotfix_schema.dict()
        hotfix_schema['for_date'] = dt.date(**hotfix_schema['for_date'])
        hotfix = tables.LessonHotfix(**hotfix_schema)
        self.session.add(hotfix)
        await self.session.commit()
        return hotfix

    async def get(
            self,
            hotfix_id: int
    ) -> tables.LessonHotfix:
        query = select(tables.LessonHotfix).filter_by(hotfix_id=hotfix_id)
        return await self.session.scalar(query)

    async def get_state(
            self, 
            lesson_id: int = None, 
            for_date: dt.date = None
) -> list[dict[str, Any]]:
        query = select(tables.LessonHotfix)
        if lesson_id is not None:
            query = query.filter_by(lesson_id=lesson_id)
        if for_date is not None:
            query = query.filter_by(for_date=for_date)

        hotfixes = await self.session.scalars(query)
        exclude = ('_sa_instance_state', 'hotfix_id', 'for_date')
        hotfixes = [dict([(k, v) for k, v in hf.__dict__.items() 
            if v is not None and k not in exclude]) for hf in hotfixes]
        return hotfixes

    async def hotfix_lessons(
            self,
            lessons_list: schemas.lessons.LessonList
    ):
        """
        Raise http 404 if has hotfix for not exist lessons for day"""
        lessons_day = dt.date.today() + \
                dt.timedelta(days=(lessons_list.lessons[0].weekday - dt.date.today().weekday()) % 7)
        hotfixes = await self.get_state(for_date=lessons_day)
        if hotfixes:  # TODO: Add support for DoubleLesson
            if any([hf.get('lesson_id') is None and not hf['is_existing'] for hf in hotfixes]):
                return schemas.lessons.LessonList(lessons=[])
            lessons = []
            for lesson in lessons_list.lessons:
                existing = True
                if lesson.lesson_id in [hf['lesson_id'] for hf in hotfixes]:
                    lesson_hotfixes = [hf for hf in hotfixes if hf['lesson_id'] == lesson.lesson_id]
                    lesson = lesson.dict()
                    for hotfix in lesson_hotfixes:
                        existing = hotfix.pop('is_existing')
                        lesson = lesson | hotfix
                    lesson = schemas.lessons.Lesson(**lesson)
                if existing:
                    lessons.append(lesson)
            lessons_list.lessons = lessons
        return lessons_list

    async def delete(self, hotfix_id: int):
        hotfix = await self.get(hotfix_id)
        await self.session.delete(hotfix)
        await self.session.commit()
