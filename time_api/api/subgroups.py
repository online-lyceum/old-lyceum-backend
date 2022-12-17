import logging
from typing import Optional

from fastapi import APIRouter, Depends

from time_api import schemas
from time_api.services.subgroups import SubgroupService


logger = logging.getLogger(__name__)
router = APIRouter(
    prefix='/api/subgroups',
    tags=['Subgroups'],
)


@router.get(
    '',
    response_model=schemas.subgroups.SubgroupList
)
async def get_subgroups(
        class_id: Optional[int] = None,
        service: SubgroupService = Depends(SubgroupService)
):
    subgroups = await service.get_list(class_id=class_id)
    return schemas.subgroups.SubgroupList(
        class_id=class_id,
        subgroups=subgroups
    )


@router.post(
    '',
    response_model=schemas.subgroups.Subgroup,
    status_code=201,
    responses={
        200: {
            'model': schemas.subgroups.Subgroup,
            'description': 'Объект уже существует'
        }
    }
)
async def create_subgroup(
        subgroup: schemas.subgroups.SubgroupCreate,
        service: SubgroupService = Depends(SubgroupService)
):
    return await service.create(subgroup)
