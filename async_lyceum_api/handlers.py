from async_lyceum_api.db import db_manager
from async_lyceum_api.db.base import get_session
from async_lyceum_api import forms

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get('/', response_model=forms.Message)
async def get_hello_msg():
    return forms.Message(msg='Hello from FastAPI and Lawrence')


@router.get('/school', response_model=forms.SchoolList)
async def get_schools(session: AsyncSession = Depends(get_session)):
    res = await db_manager.get_school_list(session)
    schools = []
    async for school, in res:
        schools.append(
            forms.School(
                school_id=school.school_id,
                name=school.name,
                address=school.address
            )
        )
    return forms.SchoolList(schools=schools)


@router.post('/school', response_model=forms.School)
async def create_school(school: forms.SchoolWithoutID,
                        session: AsyncSession = Depends(get_session)):
    new_school = await db_manager.add_school(session, **dict(school))
    return forms.School(
        school_id=new_school.school_id,
        name=new_school.name,
        address=new_school.address
    )


@router.get('/school/{school_id}/class', response_model=forms.ClassList)
async def get_classes(school_id: int,
                      session: AsyncSession = Depends(get_session)):
    res = await db_manager.get_classes(session, school_id=school_id)
    print(f"{res=}")
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


@router.post('/school/{school_id}/class', response_model=forms.Class)
async def create_class(school_id: int, class_: forms.ClassWithoutID,
                       session: AsyncSession = Depends(get_session)):
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


@router.post('/class/{class_id}/subgroup', response_model=forms.Subgroup)
async def create_subgroup(subgroup: forms.SubgroupWithoutID, class_id: int,
                          session: AsyncSession = Depends(get_session)):
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


@router.post('/school/{school_id}/lesson', response_model=forms.Lesson)
async def create_lesson(school_id: int, lesson: forms.LessonWithoutID,
                        session: AsyncSession = Depends(get_session)):
    lesson = await db_manager.create_lesson(
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
        teacher_id=lesson.teacher_id
    )


@router.post('/subgroup/{subgroup_id}/lesson',
             response_model=forms.LessonOfGroup)
async def add_lesson(subgroup_id: int, lesson: forms.OnlyLessonID,
                     session: AsyncSession = Depends(get_session)):
    res = await db_manager.add_lesson_to_subgroup(session, lesson.lesson_id,
                                                  subgroup_id)
    return forms.LessonOfGroup(
        subgroup_id=res.subgroup_id,
        lesson_id=res.lesson_id
    )


@router.get('/subgroup/{subgroup_id}/lesson', response_model=forms.LessonList)
async def get_lessons(subgroup_id: int,
                      session: AsyncSession = Depends(get_session)):
    lessons = await db_manager.get_lessons_by_subgroup_id(session, subgroup_id)
    format_lessons = []
    async for lesson, in lessons:
        format_lessons.append(forms.Lesson(
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
            teacher_id=lesson.teacher_id
        ))
    return forms.LessonList(subgroup_id=subgroup_id, lessons=format_lessons)


@router.get('/class/{class_id}/lesson',
            response_model=forms.LessonListByClassID)
async def get_lessons(class_id: int,
                      session: AsyncSession = Depends(get_session)):
    res = await db_manager.get_lessons_by_class_id(session, class_id)
    lessons = []
    async for lesson, in res:
        lesson_form = forms.Lesson(name=lesson.name,
                                   start_time=forms.Time(
                                       hour=lesson.start_time.hour,
                                       minute=lesson.start_time.minute),
                                   end_time=forms.Time(
                                       hour=lesson.end_time.hour,
                                       minute=lesson.end_time.minute),
                                   week=lesson.week,
                                   weekday=lesson.weekday,
                                   teacher_id=lesson.teacher_id,
                                   lesson_id=lesson.lesson_id)
        lessons.append(lesson_form)
    return forms.LessonListByClassID(class_id=class_id, lessons=lessons)


@router.post('/subgroup/{subgroup_id}', response_model=forms.Message)
async def delete_subgroup(subgroup_id: int, session: AsyncSession = Depends(get_session)):
    await db_manager.delete_subgroup(session, subgroup_id)
    return forms.Message(msg='Delete subgroup')
