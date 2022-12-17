import logging
from typing import Optional

from sqlalchemy import select, exc
from fastapi import status, HTTPException

from .base import BaseService
from time_api.db import tables
from time_api.schemas.subgroups import SubgroupCreate


logger = logging.getLogger(__name__)


class SubgroupService(BaseService):
    async def get_list(self, class_id: Optional[int]) -> list[tables.Subgroup]:
        query = select(tables.Subgroup).filter_by(class_id=class_id)
        subgroups = list(await self.session.scalars(query))
        if not subgroups:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return subgroups

    async def get(
            self, *,
            class_id: int = None,
            subgroup_schema: SubgroupCreate = None
    ):
        query = select(tables.Subgroup)

        if class_id is not None:
            query = query.filter_by(
                class_id=class_id
            )

        if subgroup_schema is not None:
            query = query.filter_by(
                class_id=subgroup_schema.class_id,
                name=subgroup_schema.name
            )

        subgroup = await self.session.scalar(query)
        if subgroup is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return subgroup

    async def create(self, subgroup_schema: SubgroupCreate):
        try:
            new_subgroup = tables.Subgroup(**subgroup_schema.dict())
            self.session.add(new_subgroup)
            await self.session.commit()
        except exc.IntegrityError:
            await self.session.rollback()
            new_subgroup = await self.get(subgroup_schema=subgroup_schema)
        return new_subgroup
