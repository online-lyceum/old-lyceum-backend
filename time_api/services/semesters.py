import logging
import datetime as dt
from typing import Optional

from sqlalchemy import select
from fastapi import status, HTTPException

from .base import BaseService
from time_api.db import tables
from time_api import schemas


logger = logging.getLogger(__name__)


class SemesterService(BaseService):
    async def get_list(
            self
    ) -> schemas.semesters.SemesterList:
        return schemas.semesters.SemesterList(
            semesters=await self._get_list()
        )

    async def _get_list(
            self
    ) -> list[tables.Semester]:
        query = select(tables.Semester)
        semesters = list(await self.session.scalars(query))
        if not semesters:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return semesters

    async def _get_week(
            self,
            start_date:
            dt.date,
            week_reverse: bool
    ) -> bool:
        days = (dt.date.today() - start_date).days
        week = (days % 7 + week_reverse) % 2
        return bool(week)

    async def get_current(
            self
    ) -> schemas.semesters.CurrentSemester:

        query = select(tables.Semester).filter(
            tables.Semester.start_date <= dt.date.today()
        ).filter(
            tables.Semester.end_date >= dt.date.today()
        )

        semester = await self.session.scalar(query)
        if semester is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        week: Optional[bool] = None
        if semester.week_reverse is not None:
            week = await self._get_week(
                start_date=semester.start_date,
                week_reverse=semester.week_reverse
            )

        return schemas.semesters.CurrentSemester(
            semester=semester,
            week=week
        )

    async def get(
            self, *,
            semester_id: int
    ) -> tables.Semester:
        query = select(tables.Semester)

        if semester_id is not None:
            query = query.filter_by(
                semester_id=semester_id
            )

        semester = await self.session.scalar(query)
        if semester is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return semester

    async def create(
            self,
            semester_schema: schemas.semesters.SemesterCreate
    ):
        dct = semester_schema.dict()
        dct['start_date'] = dt.date(**dct['start_date'])
        dct['end_date'] = dt.date(**dct['end_date'])
        new_semester = tables.Semester(**dct)
        self.session.add(new_semester)
        await self.session.commit()
        return new_semester

    async def delete(
            self,
            semester_id: int
    ):
        semester = await self.get(semester_id=semester_id)
        await self.session.delete(semester)
        await self.session.commit()
