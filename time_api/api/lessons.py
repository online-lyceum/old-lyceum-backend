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
        lesson_service: LessonService = Depends(LessonService)
):
    return await lesson_service.get_list(
        class_id=class_id,
        subgroup_id=subgroup_id
    )


@router.get(
    '/today',
    response_model=schemas.lessons.LessonList
)
async def get_today_lessons(
        subgroup_id: Optional[int] = None,
        class_id: Optional[int] = None,
        lesson_service: LessonService = Depends(LessonService)
):
    return await lesson_service.get_today_list(
        class_id=class_id,
        subgroup_id=subgroup_id
    )


@router.get(
    '/weekday',
    response_model=schemas.lessons.LessonList
)
async def get_weekday_lessons(
        weekday: int,
        subgroup_id: Optional[int] = None,
        class_id: Optional[int] = None,
        is_odd_week: Optional[bool] = None,
        lesson_service: LessonService = Depends(LessonService)
):
    return await lesson_service.get_weekday_list(
        weekday=weekday,
        class_id=class_id,
        subgroup_id=subgroup_id,
        is_odd_week=is_odd_week
    )


@router.get(
    '/nearest_day',
    response_model=schemas.lessons.LessonList
)
async def get_nearest_lessons(
        subgroup_id: Optional[int] = None,
        class_id: Optional[int] = None,
        lesson_service: LessonService = Depends(LessonService)
):
    return await lesson_service.get_nearest_weekday_list(
        class_id=class_id,
        subgroup_id=subgroup_id
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
async def create_lesson(
        lesson: schemas.lessons.LessonCreate,
        lesson_service: LessonService = Depends(LessonService)
):
    return await lesson_service.create(lesson)


@router.post(
    '/subgroups',
    response_model=schemas.subgroups_lessons.LessonSubgroup,
    status_code=201,
    responses={
        200: {
            'model': schemas.subgroups_lessons.LessonSubgroup,
            'description': 'Объект уже существует'
        }
    }
)
async def add_subgroup_to_lesson(
        subgroup_lesson: schemas.subgroups_lessons.LessonSubgroupCreate,
        lesson_service: LessonService = Depends(LessonService)
):
    return await lesson_service.add_subgroup_to_lesson(
        subgroup_lesson=subgroup_lesson
    )


@router.delete(
    '/{lesson_id}',
    status_code=204
)
async def delete_lesson(
        lesson_id: int,
        lesson_service: LessonService = Depends(LessonService)
):
    return await lesson_service.delete(lesson_id)
