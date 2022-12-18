import logging
from typing import Optional

from fastapi import APIRouter, Depends

from time_api import schemas
from time_api.services.lessons import LessonService


logger = logging.getLogger(__name__)
router = APIRouter(
    prefix='/api/lessons',
    tags=['Lessons'],
)


@router.get(
    '',
    response_model=schemas.lessons.LessonList
)
async def get_lessons(
        subgroup_id: Optional[int] = None,
        class_id: Optional[int] = None,
        service: LessonService = Depends(LessonService)
):
    lessons = await service.get_list(
        class_id=class_id,
        subgroup_id=subgroup_id
    )
    return schemas.lessons.LessonList(
        lessons=lessons
    )


@router.get(
    '/today',
    response_model=schemas.lessons.LessonList
)
async def get_today_lessons(
        subgroup_id: Optional[int] = None,
        class_id: Optional[int] = None,
        service: LessonService = Depends(LessonService)
):
    lessons = await service.get_list(
        class_id=class_id,
        subgroup_id=subgroup_id
    )
    return schemas.lessons.LessonList(
        lessons=lessons
    )


@router.post(
    '',
    response_model=schemas.lessons.Lesson,
    status_code=201,
    responses={
        200: {
            'model': schemas.lessons.Lesson,
            'description': 'Объект уже существует'
        }
    }
)
async def create_class(
        lesson: schemas.lessons.LessonCreate,
        service: LessonService = Depends(LessonService)
):
    return await service.create(lesson)


