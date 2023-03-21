import logging

from sqlalchemy import select, exc
from fastapi import HTTPException, status

from .base import BaseService
from time_api.db import tables
from time_api import schemas


logger = logging.getLogger(__name__)


class SchoolService(BaseService):
    async def get_list(self):
        return schemas.schools.SchoolList(
            schools=await self._get_list()
        )

    async def _get_list(self) -> list[tables.School]:
        query = select(tables.School)
        return list(await self.session.scalars(query))

    async def get(
            self, *,
            school_id: int = None,
            school_schema: schemas.schools.SchoolCreate = None
    ) -> tables.School:

        query = select(tables.School)

        if school_id is not None:
            query = query.filter_by(school_id=school_id)

        if school_schema is not None:
            query = query.filter_by(
                name=school_schema.name,
                address=school_schema.address
            )

        school = await self.session.scalar(query)
        if school is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        return school

    async def create(
            self,
            school_schema: schemas.schools.SchoolCreate
    ) -> tables.School:

        try:
            school = tables.School(**school_schema.dict())
            self.session.add(school)
            await self.session.commit()

        except exc.IntegrityError:
            await self.session.rollback()
            self.response.status_code = status.HTTP_200_OK

            school = await self.get(school_schema=school_schema)

        return school

    async def delete(
            self,
            school_id: int,
    ):

        school = await self.get(school_id=school_id)
        await self.session.delete(school)
        await self.session.commit()

