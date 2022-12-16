import logging

from sqlalchemy import select, exc
from fastapi import status, HTTPException

from .base import BaseService
from time_api.db import tables
from time_api.schemas.classes import ClassCreate


logger = logging.getLogger(__name__)


class ClassService(BaseService):
    async def get_list(self, school_id: int) -> list[tables.Class]:
        query = select(tables.Class).filter_by(school_id=school_id)
        classes = list(await self.session.scalars(query))
        if not classes:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return classes

    async def get(
            self, *,
            class_schema: ClassCreate
    ):
        query = select(tables.Class).filter_by(
            number=class_schema.number,
            letter=class_schema.letter
        )
        new_class = await self.session.scalar(query)
        if new_class is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return new_class

    async def create(self, class_schema: ClassCreate):
        try:
            new_class = tables.Class(**class_schema.dict())
            self.session.add(new_class)
            await self.session.commit()
        except exc.IntegrityError:
            await self.session.rollback()
            new_class = await self.get(class_schema=class_schema)
        return new_class
