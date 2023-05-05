from typing import Optional, Union 
from loguru import logger

from fastapi import APIRouter, Depends, HTTPException

from time_api import schemas
from time_api.services.lessons import LessonService
from time_api.services.lessons_hotfix import LessonHotfixService
from time_api.services.auth import authenticate, AccessLevel 

router = APIRouter(
    prefix='/api/lessons',
    tags=['Lessons'],
)


@router.get(
    '',
    response_model=(
            schemas.lessons.LessonListWithDouble | schemas.lessons.LessonList),
    description='''
        Return one of lessons_list or lessons_list with doubled lessons
        Return depends on do_double query parameter
    '''
)
async def get_lessons(
        subgroup_id: Optional[int] = None,
        class_id: Optional[int] = None,
        teacher_id: int | None = None,
        weekday: Optional[int] = None,
        do_double: Optional[bool] = False,
        service: LessonService = Depends(LessonService)
):
    return await service.get_list(
        class_id=class_id,
        weekday=weekday,
        subgroup_id=subgroup_id,
        do_double=do_double,
        teacher_id=teacher_id
    )


@router.get(
    '/today',
    response_model=schemas.lessons.LessonList,
    deprecated=True
)
async def get_today_lessons(
        subgroup_id: Optional[int] = None,
        class_id: Optional[int] = None,
        service: LessonService = Depends(LessonService)
):
    return await service.get_today_list(
        class_id=class_id,
        subgroup_id=subgroup_id
    )


@router.get(
    '/weekday',
    response_model=schemas.lessons.LessonList,
    deprecated=True
)
async def get_weekday_lessons(
        weekday: Optional[int] = None,
        subgroup_id: Optional[int] = None,
        class_id: Optional[int] = None,
        service: LessonService = Depends(LessonService)
):
    return await service.get_weekday_list(
        weekday=weekday,
        class_id=class_id,
        subgroup_id=subgroup_id
    )


@router.get(
    '/nearest_day',
    response_model=Union[
        schemas.lessons.LessonList,
        schemas.lessons.LessonListWithDouble
    ]
)
async def get_nearest_lessons(
        subgroup_id: Optional[int] = None,
        class_id: Optional[int] = None,
        teacher_id: int | None = None,
        do_double: bool = False,
        service: LessonService = Depends(LessonService)
):
    return await service.get_nearest_list(
        class_id=class_id,
        subgroup_id=subgroup_id,
        do_double=do_double,
        teacher_id=teacher_id
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
        _=Depends(authenticate.teacher()),
        service: LessonService = Depends(LessonService)
):
    return await service.create(lesson)


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
        _=Depends(authenticate.teacher()),
        service: LessonService = Depends(LessonService)
):
    return await service.add_subgroup_to_lesson(subgroup_lesson=subgroup_lesson)


@router.patch(
    '/',
    description="""
        Create hotfix for day or lesson in day
        If is_existing is False and lesson_id is None, cancel all lessons at for_day
        and require field school_id.
        
        school_id: enter only if you cancel all lessons at for_day
    """,
    status_code=201,
    response_model=schemas.lessons.LessonHotfix
)
async def add_lesson_hotfix(
        lesson_hotfix: schemas.lessons.LessonHotfixCreate,
        auth_data=Depends(authenticate.class_president()),
        service: LessonHotfixService = Depends(LessonHotfixService)
):
    # TODO Check existing school_id and lesson_id
    if not lesson_hotfix.is_existing and lesson_hotfix.lesson_id is None:
        if lesson_hotfix.school_id is None:
            raise HTTPException(status_code=422, detail="Require school_id")
        if auth_data.get('access_level', AccessLevel.unauthorized) < AccessLevel.teacher:
            raise HTTPException(status_code=401)
    return await service.create(lesson_hotfix)


@router.delete(
    '/hotfix/{hotfix_id}',
    status_code=204
)
async def delete_lesson_hotfix(
        hotfix_id: int,
        _=Depends(authenticate.class_president()),
        service: LessonHotfixService = Depends(LessonHotfixService)
):
    return await service.delete(hotfix_id)
