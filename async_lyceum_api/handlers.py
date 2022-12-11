import logging


from async_lyceum_api.db import db_manager
from async_lyceum_api.db.base import get_session
from async_lyceum_api import forms

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, AsyncResult

from fastapi import Response

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/api')


async def transform_db_lessons_to_lesson_forms(
        lessons: AsyncResult | list) -> list[forms.LessonType]:
    if isinstance(lessons, AsyncResult):
        return [_transform_db_lesson_to_lesson_form(lesson, teacher) async for lesson, teacher in lessons]
    else:
        return [_transform_db_lesson_to_lesson_form(lesson, teacher) for lesson, teacher in lessons]


def _transform_db_lesson_to_lesson_form(lesson: db_manager.db.Lesson,
                                        teacher: db_manager.db.Teacher):
    logger.debug(f'{type(lesson)=}')
    return forms.Lesson(
            lesson_id=lesson.lesson_id,
            name=lesson.name,
            start_time=forms.Time(
                hour=lesson.start_time.hour,
                minute=lesson.start_time.minute
            ),
            end_time=forms.Time(
                hour=lesson.end_time.hour,
                minute=lesson.end_time.minute
            ),
            week=lesson.week,
            weekday=lesson.weekday,
            teacher=forms.Teacher(
                teacher_id=teacher.teacher_id,
                name=teacher.name
            )
        )


@router.get('/', response_model=forms.Message)
async def get_hello_msg():
    return forms.Message(msg='Hello from FastAPI and Lawrence')


@router.get('/city', response_model=forms.CityList)
async def get_cities(session: AsyncSession = Depends(get_session)):
    cities = []
    async for city, in await db_manager.get_cities(session):
        cities.append(city)
    return forms.CityList(cities=cities)


@router.get('/school', response_model=forms.SchoolList)
async def get_schools(session: AsyncSession = Depends(get_session)):
    res = await db_manager.get_school_list(session)
    schools = []
    async for school_id, name, city, place in res:
        schools.append(
            forms.School(
                school_id=school_id,
                name=name,
                city=city,
                place=place
            )
        )
    return forms.SchoolList(schools=schools)


@router.post('/school', response_model=forms.School, status_code=201)
async def create_school(school: forms.SchoolWithoutID,
                        session: AsyncSession = Depends(get_session),
                        response: Response = Response):
    if await db_manager.school_exist(session, **dict(school)):
        response.status_code = 200

    new_school, address = await db_manager.add_school_with_address(session, **dict(school))

    return forms.School(
        school_id=new_school.school_id,
        name=new_school.name,
        city=address.city,
        place=address.place
    )


@router.get('/school/{school_id}/class', response_model=forms.ClassList)
async def get_classes(school_id: int,
                      session: AsyncSession = Depends(get_session)):
    res = await db_manager.get_classes(session, school_id=school_id)
    classes = []
    async for x in res:
        classes.append(
            forms.Class(
                class_id=x[0],
                number=x[1],
                letter=x[2],
                class_type=x[3]
            )
        )
    return forms.ClassList(school_id=school_id, classes=classes)


@router.post('/school/{school_id}/class', response_model=forms.Class, status_code=201)
async def create_class(school_id: int, class_: forms.ClassWithoutID,
                       session: AsyncSession = Depends(get_session),
                       response: Response = Response):
    if await db_manager.class_exist(session, school_id=school_id, **dict(class_)):
        response.status_code = 200

    new_class, class_type = await db_manager.add_class(
        session,
        school_id=school_id,
        **dict(class_)
    )
    return forms.Class(
        class_id=new_class.class_id,
        number=new_class.number,
        letter=new_class.letter,
        class_type=class_type
    )


@router.post('/class/{class_id}/subgroup', response_model=forms.Subgroup, status_code=201)
async def create_subgroup(subgroup: forms.SubgroupWithoutID, class_id: int,
                          session: AsyncSession = Depends(get_session),
                          response: Response = Response):
    if await db_manager.subgroup_exist(session,
                                       class_id=class_id,
                                       name=subgroup.name):
        response.status_code = 200

    new_subgroup = await db_manager.create_subgroup(
        session,
        class_id=class_id,
        name=subgroup.name
    )
    return forms.Subgroup(
        subgroup_id=new_subgroup.subgroup_id,
        name=new_subgroup.name
    )


@router.get('/class/{class_id}/subgroup', response_model=forms.SubgroupList)
async def get_subgroups(class_id: int,
                        session: AsyncSession = Depends(get_session)):
    res = await db_manager.get_subgroups(session, class_id=class_id)
    subgroups = []
    async for subgroup, in res:
        subgroups.append(forms.Subgroup(
            subgroup_id=subgroup.subgroup_id,
            class_id=subgroup.class_id,
            name=subgroup.name
        ))
    return forms.SubgroupList(
        class_id=class_id,
        subgroups=subgroups
    )


@router.post('/teacher', response_model=forms.Teacher)
async def create_teacher(teacher: forms.TeacherWithoutID,
                         session: AsyncSession = Depends(get_session)):
    res = await db_manager.create_teacher(session, name=teacher.name)
    return forms.Teacher(
        teacher_id=res.teacher_id,
        name=res.name
    )


@router.get('/teacher', response_model=forms.TeacherList)
async def get_teachers(session: AsyncSession = Depends(get_session)):
    res = await db_manager.get_teachers(session)
    teachers = []
    async for teacher, in res:
        teachers.append(forms.Teacher(name=teacher.name))
    return forms.TeacherList(teachers=teachers)


@router.post('/school/{school_id}/lesson', response_model=forms.Lesson, status_code=201)
async def create_lesson(school_id: int, lesson: forms.LessonWithoutIDWithTeacherID,
                        session: AsyncSession = Depends(get_session),
                        response: Response = Response):
    if await db_manager.lesson_exist(session, school_id,
                                     lesson.name, dict(lesson.start_time),
                                     dict(lesson.end_time), lesson.week,
                                     lesson.weekday, lesson.teacher_id):
        response.status_code = 200
    lesson, teacher = await db_manager.create_lesson_and_get_teacher(
        session, school_id=school_id,
        name=lesson.name, start_time=dict(lesson.start_time),
        end_time=dict(lesson.end_time), week=lesson.week,
        weekday=lesson.weekday, teacher_id=lesson.teacher_id
    )
    return forms.Lesson(
        school_id=school_id,
        lesson_id=lesson.lesson_id,
        name=lesson.name,
        start_time=forms.Time(hour=lesson.start_time.hour,
                              minute=lesson.start_time.minute),
        end_time=forms.Time(hour=lesson.end_time.hour,
                            minute=lesson.end_time.minute),
        week=lesson.week,
        weekday=lesson.weekday,
        teacher=forms.Teacher(
            name=teacher.name,
            teacher_id=teacher.teacher_id
        )
    )


@router.post('/subgroup/{subgroup_id}/lesson',
             response_model=forms.LessonOfGroup, status_code=201)
async def add_lesson(subgroup_id: int, lesson: forms.OnlyLessonID,
                     session: AsyncSession = Depends(get_session),
                     response: Response = Response):
    if await db_manager.subgroup_lesson_exist(session, lesson.lesson_id,
                                              subgroup_id):
        response.status_code = 200
    res = await db_manager.add_lesson_to_subgroup(session, lesson.lesson_id,
                                                  subgroup_id)
    return forms.LessonOfGroup(
        subgroup_id=res.subgroup_id,
        lesson_id=res.lesson_id
    )


@router.get('/subgroup/{subgroup_id}/lesson', response_model=forms.LessonList)
async def get_lessons(subgroup_id: int,
                      session: AsyncSession = Depends(get_session)):
    lesson_list = db_manager.LessonList(session, subgroup_id)
    db_lesson_rows = await lesson_list.get_all_lessons()
    lesson_forms = await transform_db_lessons_to_lesson_forms(db_lesson_rows)
    return forms.LessonList(subgroup_id=subgroup_id, lessons=lesson_forms)


@router.get('/class/{class_id}/lesson',
            response_model=forms.LessonListByClassID)
async def get_lessons(class_id: int,
                      session: AsyncSession = Depends(get_session)):
    db_lesson_rows = await db_manager.get_lessons_by_class_id(session, class_id)
    lessons = await transform_db_lessons_to_lesson_forms(db_lesson_rows)
    return forms.LessonListByClassID(class_id=class_id, lessons=lessons)


@router.get('/subgroup/{subgroup_id}/lessons_to_show_today',
            response_model=forms.DaySubgroupLessons)
async def get_today_lessons(subgroup_id: int,
                            session: AsyncSession = Depends(get_session)):
    lesson_list = db_manager.LessonList(session, subgroup_id)
    weekday, db_lesson_rows = await lesson_list.get_current_or_next_day_with_lessons()
    lessons = await transform_db_lessons_to_lesson_forms(db_lesson_rows)
    logger.debug(f'{lessons=}')
    return forms.DaySubgroupLessons(
        weekday=weekday,
        week=0,
        lessons=lessons,
        subgroup_id=subgroup_id
    )


@router.delete('/subgroup/{subgroup_id}/lesson/{lesson_id}', status_code=204)
async def delete_subgroup_lesson(subgroup_id: int, lesson_id: int,
                                 session: AsyncSession = Depends(get_session)):
    await db_manager.delete_subgroup_lesson(session, subgroup_id, lesson_id)


@router.delete('/lesson/{lesson_id}', status_code=204)
async def delete_lesson(lesson_id: int,
                        session: AsyncSession = Depends(get_session)):
    await db_manager.delete_lesson(session, lesson_id)


@router.delete('/subgroup/{subgroup_id}', status_code=204)
async def delete_subgroup(subgroup_id: int,
                          session: AsyncSession = Depends(get_session)):
    await db_manager.delete_subgroup(session, subgroup_id)


@router.delete('/class/{class_id}', status_code=204)
async def delete_class(class_id: int,
                       session: AsyncSession = Depends(get_session)):
    await db_manager.delete_class(session, class_id)


@router.delete('/school/{school_id}', status_code=204)
async def delete_school(school_id: int,
                        session: AsyncSession = Depends(get_session)):
    await db_manager.delete_school(session, school_id)
