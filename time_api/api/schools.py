import logging

from fastapi import APIRouter, Depends

from time_api import schemas
from time_api.services.schools import SchoolService


logger = logging.getLogger(__name__)
router = APIRouter(
    prefix='/api/schools',
    tags=['schools'],
)


@router.get(
    '/',
    response_model=schemas.schools.SchoolList,
    tags=['Get']
)
async def get_schools(
       service: SchoolService = Depends(SchoolService)
):
    schools = await service.get_list()
    return schemas.schools.SchoolList(
        schools=schools
    )


@router.post(
    '/',
    response_model=schemas.schools.School,
    status_code=201,
    responses={
        200: {
            'model': schemas.schools.School,
            'description': 'Объект уже существует'
        }
    },
    tags=['Create']
)
async def create_school(
        school: schemas.schools.SchoolCreate,
        service: SchoolService = Depends(SchoolService)
):
    school = await service.create(school)
    return school
