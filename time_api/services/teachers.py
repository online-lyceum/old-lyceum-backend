import logging

from sqlalchemy import select
from fastapi import status, HTTPException

from .base import BaseService
from time_api.db import tables
from time_api.schemas.teachers import TeacherCreate


logger = logging.getLogger(__name__)


class TeacherService(BaseService):
    async def get_list(self) -> list[tables.Teacher]:
        query = select(tables.Teacher)
        teachers = list(await self.session.scalars(query))
        if not teachers:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return teachers

    async def get(
            self, *,
            teacher_id: int
    ) -> tables.Teacher:
        query = select(tables.Teacher)

        if teacher_id is not None:
            query = query.filter_by(
                teacher_id=teacher_id
            )

        teacher = await self.session.scalar(query)
        if teacher is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return teacher

    async def create(self, teacher_schema: TeacherCreate):
        new_teacher = tables.Teacher(**teacher_schema.dict())
        self.session.add(new_teacher)
        await self.session.commit()
        return new_teacher
