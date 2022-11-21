from async_lyceum_api.db import db_manager
from async_lyceum_api.db.base import get_session
from async_lyceum_api.forms import *

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get('/class/{class_id}/lesson', response_model=LessonListByClassID)
async def get_lessons(class_id: int,
                      session: AsyncSession = Depends(get_session)):
    res = await db_manager.get_lessons_by_class_id(session, class_id)
    lessons = []
    async for lesson, in res:
        lesson_form = Lesson(name=lesson.name,
                             start_time=Time(hour=lesson.start_time.hour,
                                             minute=lesson.start_time.minute),
                             end_time=Time(hour=lesson.end_time.hour,
                                           minute=lesson.end_time.minute),
                             week=lesson.week,
                             weekday=lesson.weekday,
                             teacher_id=lesson.teacher_id,
                             lesson_id=lesson.lesson_id)
        lessons.append(lesson_form)
    return LessonListByClassID(class_id=class_id, lessons=lessons)


@router.get('/', response_model=Message)
async def get_hello_msg():
    return Message(msg='Hello from FastAPI and Lawrence')


@router.get('/school', response_model=SchoolList)
async def get_schools(session: AsyncSession = Depends(get_session)):
    res = await db_manager.get_school_list(session)
    schools = []
    async for school, in res:
        schools.append(
            School(
                school_id=school.school_id,
                name=school.name,
                address=school.address
            )
        )
    return SchoolList(schools=schools)


@router.post('/school', response_model=School)
async def create_school(school: SchoolWithoutID,
                        session: AsyncSession = Depends(get_session)):
    new_school = await db_manager.add_school(session, **dict(school))
    return School(
        school_id=new_school.school_id,
        name=new_school.name,
        address=new_school.address
    )


@router.get('/school/{school_id}/class', response_model=ClassList)
async def get_classes(school_id: int,
                      session: AsyncSession = Depends(get_session)):
    res = await db_manager.get_classes(session, school_id=school_id)
    print(f"{res=}")
    classes = []
    async for x in res:
        classes.append(
            Class(
                class_id=x[0],
                number=x[1],
                letter=x[2],
                class_type=x[3]
            )
        )
    return ClassList(school_id=school_id, classes=classes)


@router.post('/school/{school_id}/class', response_model=Class)
async def create_class(school_id: int, class_: ClassWithoutID,
                       session: AsyncSession = Depends(get_session)):
    new_class, class_type = await db_manager.add_class(
        session,
        school_id=school_id,
        **dict(class_)
    )
    return Class(
        class_id=new_class.class_id,
        number=new_class.number,
        letter=new_class.letter,
        class_type=class_type
    )


@router.post('/class/{class_id}/subgroup', response_model=Subgroup)
async def create_subgroup(subgroup: SubgroupWithoutID, class_id: int,
                          session: AsyncSession = Depends(get_session)):
    new_subgroup = await db_manager.create_subgroup(
        session,
        class_id=class_id,
        name=subgroup.name
    )
    return Subgroup(
        subgroup_id=new_subgroup.subgroup_id,
        name=new_subgroup.name
    )


@router.get('/class/{class_id}/subgroup', response_model=SubgroupList)
async def get_subgroups(class_id: int,
                        session: AsyncSession = Depends(get_session)):
    res = await db_manager.get_subgroups(session, class_id=class_id)
    subgroups = []
    async for subgroup, in res:
        subgroups.append(Subgroup(
            subgroup_id=subgroup.subgroup_id,
            class_id=subgroup.class_id,
            name=subgroup.name
        ))
    return SubgroupList(
        class_id=class_id,
        subgroups=subgroups
    )


@router.post('/teacher', response_model=Teacher)
async def create_teacher(teacher: TeacherWithoutID,
                         session: AsyncSession = Depends(get_session)):
    res = await db_manager.create_teacher(session, name=teacher.name)
    return Teacher(
        teacher_id=res.teacher_id,
        name=res.name
    )


@router.get('/teacher', response_model=TeacherList)
async def get_teachers(session: AsyncSession = Depends(get_session)):
    res = await db_manager.get_teachers(session)
    teachers = []
    async for teacher, in res:
        teachers.append(Teacher(name=teacher.name))
    return TeacherList(teachers=teachers)


@router.post('/school/{school_id}/lesson', response_model=Lesson)
async def create_lesson(school_id: int, lesson: LessonWithoutID,
                        session: AsyncSession = Depends(get_session)):
    lesson = await db_manager.create_lesson(
        session, school_id=school_id,
        name=lesson.name, start_time=dict(lesson.start_time),
        end_time=dict(lesson.end_time), week=lesson.week,
        weekday=lesson.weekday, teacher_id=lesson.teacher_id
    )
    return Lesson(
        school_id=school_id,
        lesson_id=lesson.lesson_id,
        name=lesson.name,
        start_time=Time(hour=lesson.start_time.hour,
                        minute=lesson.start_time.minute),
        end_time=Time(hour=lesson.end_time.hour,
                      minute=lesson.end_time.minute),
        week=lesson.week,
        weekday=lesson.weekday,
        teacher_id=lesson.teacher_id
    )


@router.post('/subgroup/{subgroup_id}/lesson', response_model=LessonOfGroup)
async def add_lesson(subgroup_id: int, lesson: OnlyLessonID,
                     session: AsyncSession = Depends(get_session)):
    res = await db_manager.add_lesson_to_subgroup(session, lesson.lesson_id,
                                                  subgroup_id)
    return LessonOfGroup(
        subgroup_id=res.subgroup_id,
        lesson_id=res.lesson_id
    )


@router.get('/subgroup/{subgroup_id}/lesson', response_model=LessonList)
async def get_lessons(subgroup_id: int,
                      session: AsyncSession = Depends(get_session)):
    lessons = await db_manager.get_lessons(session, subgroup_id)
    format_lessons = []
    async for lesson, in lessons:
        format_lessons.append(Lesson(
            lesson_id=lesson.lesson_id,
            name=lesson.name,
            start_time=Time(
                hour=lesson.start_time.hour,
                minute=lesson.start_time.minute
            ),
            end_time=Time(
                hour=lesson.end_time.hour,
                minute=lesson.end_time.minute
            ),
            week=lesson.week,
            weekday=lesson.weekday,
            teacher_id=lesson.teacher_id
        ))
    return LessonList(subgroup_id=subgroup_id, lessons=format_lessons)
