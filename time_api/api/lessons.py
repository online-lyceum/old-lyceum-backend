import logging
from typing import Optional

from fastapi import APIRouter, Depends

from time_api import schemas
from time_api.services.lessons import LessonService as _LessonService
from time_api.services.semesters import SemesterService as _SemesterService

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix='/api/lessons',
    tags=['Lessons'],
)


class AllService:
    def __init__(
            self,

            semester_service:
            _SemesterService = Depends(_SemesterService),

            lesson_service:
            _LessonService = Depends(_LessonService)
    ):
        self.semester = semester_service
        self.lesson = lesson_service


@router.get(
    '',
    response_model=schemas.lessons.LessonList
)
async def get_lessons(
        subgroup_id: Optional[int] = None,
        class_id: Optional[int] = None,
        service: AllService = Depends(AllService)
):
    return await service.lesson.get_list(
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
        service: AllService = Depends(AllService)
):
    return await service.lesson.get_today_list(
        class_id=class_id,
        subgroup_id=subgroup_id,
        semester_service=service.semester
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
        service: AllService = Depends(AllService)
):
    return await service.lesson.get_weekday_list(
        weekday=weekday,
        class_id=class_id,
        subgroup_id=subgroup_id,
        is_odd_week=is_odd_week,
        semester_service=service.semester
    )


@router.get(
    '/nearest_day',
    response_model=schemas.lessons.LessonList
)
async def get_nearest_lessons(
        subgroup_id: Optional[int] = None,
        class_id: Optional[int] = None,
        service: AllService = Depends(AllService)
):
    return await service.lesson.get_nearest_weekday_list(
        class_id=class_id,
        subgroup_id=subgroup_id,
        semester_service=service.semester
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
        service: AllService = Depends(AllService)
):
    return await service.lesson.create(lesson)


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
        service: AllService = Depends(AllService)
):
    return await service.lesson.add_subgroup_to_lesson(subgroup_lesson=subgroup_lesson)


@router.delete(
    '/{lesson_id}',
    status_code=204
)
async def delete_lesson(
        lesson_id: int,
        service: AllService = Depends(AllService)
):
    return await service.lesson.delete(lesson_id)
