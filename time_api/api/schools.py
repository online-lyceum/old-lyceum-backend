import logging

from fastapi import APIRouter, Depends

from time_api import schemas
from time_api.services.schools import SchoolService


logger = logging.getLogger(__name__)
router = APIRouter(
    prefix='/api/schools',
    tags=['Schools'],
)


@router.get(
    '',
    response_model=schemas.schools.SchoolList
)
async def get_schools(
       service: SchoolService = Depends(SchoolService)
):
    return await service.get_list()


@router.post(
    '',
    response_model=schemas.schools.School,
    status_code=201,
    responses={
        200: {
            'model': schemas.schools.School,
            'description': 'Объект уже существует'
        }
    }
)
async def create_school(
        school: schemas.schools.SchoolCreate,
        service: SchoolService = Depends(SchoolService)
):
    return await service.create(school)


@router.get(
    '/{school_id}',
    response_model=schemas.schools.School
)
async def get_school(
        school_id: int,
        service: SchoolService = Depends(SchoolService)
):
    return await service.get(school_id=school_id)


@router.delete(
    '/{school_id}',
    status_code=204
)
async def delete_school(
    school_id: int,
    service: SchoolService = Depends(SchoolService)
):
    return await service.delete(school_id=school_id)
