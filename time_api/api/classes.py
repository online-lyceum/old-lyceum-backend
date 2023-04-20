import logging
from typing import Optional

from fastapi import APIRouter, Depends

from time_api import schemas
from time_api.services.classes import ClassService
from time_api.services.auth import authenticate


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
    return await service.get_list(school_id)


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
        _ = Depends(authenticate()),
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


@router.delete(
    '/{class_id}',
    status_code=204
)
async def delete_class(
    class_id: int,
    service: ClassService = Depends(ClassService)
):
    return await service.delete(class_id=class_id)
