import logging

from fastapi import APIRouter, Depends

from time_api import schemas
from time_api.services.semesters import SemesterService
from time_api.services.auth import authenticate

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix='/api/semesters',
    tags=['Semesters'],
)


@router.get(
    '',
    response_model=schemas.semesters.SemesterList
)
async def get_semesters(
        service: SemesterService = Depends(SemesterService)
):
    return await service.get_list()


@router.get(
    '/current',
    response_model=schemas.semesters.CurrentSemester
)
async def get_current_semester(
        service: SemesterService = Depends(SemesterService)
):
    return await service.get_current()


@router.get(
    '/{semester_id}',
    response_model=schemas.semesters.Semester
)
async def get_semester(
        semester_id: int,
        service: SemesterService = Depends(SemesterService)
):
    return await service.get(semester_id=semester_id)


@router.post(
    '',
    response_model=schemas.semesters.Semester,
    status_code=201,
    responses={
        200: {
            'model': schemas.semesters.Semester,
            'description': 'Объект уже существует'
        }
    }
)
async def create_semester(
        semester: schemas.semesters.SemesterCreate,
        _=Depends(authenticate.teacher()),
        service: SemesterService = Depends(SemesterService)
):
    return await service.create(semester)


@router.delete(
    '/{semester_id}',
    status_code=204
)
async def delete_semester(
        semester_id: int,
        _=Depends(authenticate.teacher()),
        service: SemesterService = Depends(SemesterService)
):
    return await service.delete(semester_id=semester_id)
