import logging
from typing import Optional

from fastapi import APIRouter, Depends

from time_api import schemas
from time_api.services.classes import ClassService


logger = logging.getLogger(__name__)
router = APIRouter(
    prefix='/api/classes',
    tags=['Classes'],
)


@router.get(
    '',
    response_model=schemas.classes.ClassList
)
async def get_classes(
        school_id: Optional[int] = None,
        service: ClassService = Depends(ClassService)
):
    classes = await service.get_list(school_id)
    return schemas.classes.ClassList(
        school_id=school_id,
        classes=classes
    )


@router.post(
    '',
    response_model=schemas.classes.Class,
    status_code=201,
    responses={
        200: {
            'model': schemas.classes.Class,
            'description': 'Объект уже существует'
        }
    }
)
async def create_class(
        class_: schemas.classes.ClassCreate,
        service: ClassService = Depends(ClassService)
):
    return await service.create(class_)


@router.get(
    '/{class_id}',
    response_model=schemas.classes.Class
)
async def get_class(
        class_id: int,
        service: ClassService = Depends(ClassService)
):
    return await service.get(class_id=class_id)
