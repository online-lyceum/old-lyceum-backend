import datetime as dt
from typing import Optional, Any

from sqlalchemy import select, exc
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, HTTPException, Depends

from time_api.services.semesters import SemesterService
from time_api.services.base import BaseService
from time_api.db import tables
from time_api.schemas.lessons import LessonCreate, Lesson
from time_api import schemas
from time_api.services.teachers import TeacherService
from time_api.db.base import get_session


def _dict_to_schemas_lessons(lesson: dict):
    return Lesson(
        name=lesson['name'],
        start_time=dt.time(**lesson['start_time']),
        end_time=dt.time(**lesson['end_time']),
        is_odd_week=lesson['is_odd_week'],
        weekday=lesson['weekday'],
        room=lesson['room'],
        school_id=lesson['school_id'],
        lesson_id=lesson['lesson_id'],
        teacher=schemas.teachers.Teacher(
            **schemas.teachers.Teacher.from_orm(lesson['teacher']).dict()
        ),
        semester_id=lesson['semester_id']
    )


class LessonService(BaseService):

    def __init__(
            self,
            session: AsyncSession = Depends(get_session),
            semester_service: SemesterService = Depends(SemesterService)
    ):
        super().__init__(session=session)
        self.semester_service = semester_service

    async def get_list(
            self,
            class_id: Optional[int] = None,
            subgroup_id: Optional[int] = None,
            is_odd_week: Optional[bool] = None,
            weekday: Optional[int] = None,
            semester_id: Optional[int] = None
    ) -> schemas.lessons.LessonList:
        lessons = await self._get_list(
            class_id=class_id,
            subgroup_id=subgroup_id,
            is_odd_week=is_odd_week,
            weekday=weekday,
            semester_id=semester_id
        )
        lessons = [await self._add_teacher(lesson) for lesson in lessons]
        return schemas.lessons.LessonList(
            lessons=lessons
        )

    async def _add_teacher(
            self,
            lesson: tables.Lesson
    ) -> dict[str, Any]:
        dct = schemas.lessons.InternalLesson.from_orm(lesson).dict()
        dct['teacher'] = await self._get_teacher(lesson.teacher_id)
        return dct

    async def _get_teacher(
            self,
            teacher_id: int
    ):
        teacher_service = TeacherService(self.session, self.response)
        return await teacher_service.get(teacher_id=teacher_id)

    async def _get_list(
            self,
            class_id: Optional[int] = None,
            subgroup_id: Optional[int] = None,
            is_odd_week: Optional[bool] = None,
            weekday: Optional[int] = None,
            semester_id: Optional[int] = None
    ) -> list[tables.Class]:

        query = select(tables.Lesson)

        if subgroup_id is not None or class_id is not None:
            query = query.join(tables.LessonSubgroup)

        if subgroup_id is not None:
            query = query.filter_by(
                subgroup_id=subgroup_id
            )

        if class_id is not None:
            query = query.join(tables.Subgroup)
            query = query.filter_by(
                class_id=class_id
            )

        if is_odd_week is not None:
            query = query.filter(
                tables.Lesson.is_odd_week != (not is_odd_week)
            )

        if weekday is not None:
            query = query.filter(
                tables.Lesson.weekday == weekday
            )

        if semester_id is not None:
            query = query.filter(
                tables.Lesson.semester_id == semester_id
            )

        query = query.order_by(tables.Lesson.start_time)
        lessons = list(await self.session.scalars(query))
        if not lessons:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        return lessons

    async def get_weekday_list(
            self,
            weekday: int,
            class_id: Optional[int] = None,
            subgroup_id: Optional[int] = None,
            is_odd_week: Optional[bool] = None
    ) -> schemas.lessons.LessonList:
        semester = await self.semester_service.get_current()

        if is_odd_week is None:
            is_odd_week = semester.is_odd_week

        lessons = await self._get_list(
            class_id=class_id,
            subgroup_id=subgroup_id,
            weekday=weekday,
            semester_id=semester.semester.semester_id,
            is_odd_week=is_odd_week
        )
        lessons = [await self._add_teacher(lesson) for lesson in lessons]
        return schemas.lessons.LessonList(
            lessons=lessons
        )

    async def get_today_list(
            self,
            class_id: Optional[int] = None,
            subgroup_id: Optional[int] = None
    ) -> schemas.lessons.LessonList:
        today = dt.datetime.today().weekday()
        return await self.get_weekday_list(
            weekday=today,
            class_id=class_id,
            subgroup_id=subgroup_id
        )

    async def _get_nearest_weekday_list(
            self,
            class_id: Optional[int] = None,
            subgroup_id: Optional[int] = None
    ):
        current_semester = await self.semester_service.get_current()
        current_semester = current_semester.semester

        today = dt.datetime.today()

        is_odd_week = await self.semester_service.get_week(
            start_date=dt.date(**current_semester.start_date.dict()),
            week_reverse=current_semester.week_reverse
        )


        flag = 0
        try:
            lesson = (await self._get_list(
                semester_id=current_semester.semester_id,
                class_id=class_id,
                subgroup_id=subgroup_id,
                weekday=today.weekday(),
                is_odd_week=is_odd_week
            ))[-1]
            end_time = schemas.lessons.InternalLesson.from_orm(lesson).end_time
            if dt.time(hour=end_time.hour,
                       minute=end_time.minute) <= today.now().time():
                flag = 1
        except HTTPException:
            pass

        for weekday in range(today.weekday() + flag, 7):
            try:
                lessons = await self._get_list(
                    semester_id=current_semester.semester_id,
                    class_id=class_id,
                    subgroup_id=subgroup_id,
                    weekday=weekday,
                    is_odd_week=is_odd_week
                )
            except HTTPException:
                continue
            return lessons
        for weekday in range(0, today.weekday()):
            try:
                lessons = await self._get_list(
                    semester_id=current_semester.semester_id,
                    class_id=class_id,
                    subgroup_id=subgroup_id,
                    weekday=weekday,
                    is_odd_week=is_odd_week
                )
            except HTTPException:
                continue
            return lessons

        for weekday in range(0, today.weekday()):
            try:
                lessons = await self._get_list(
                    semester_id=current_semester.semester_id,
                    class_id=class_id,
                    subgroup_id=subgroup_id,
                    weekday=weekday,
                    is_odd_week=(not is_odd_week)
                )
            except HTTPException:
                continue
            return lessons
        for weekday in range(today.weekday(), 7):
            try:
                lessons = await self._get_list(
                    semester_id=current_semester.semester_id,
                    class_id=class_id,
                    subgroup_id=subgroup_id,
                    weekday=weekday,
                    is_odd_week=(not is_odd_week)
                )
            except HTTPException:
                continue
            return lessons
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    async def get_nearest_weekday_list(
            self,
            class_id: Optional[int] = None,
            subgroup_id: Optional[int] = None
    ):
        lessons = await self._get_nearest_weekday_list(
            class_id=class_id,
            subgroup_id=subgroup_id
        )

        lessons = [await self._add_teacher(lesson) for lesson in lessons]
        returned_lessons: list[Lesson] = []
        for lesson in lessons:
            lesson = _dict_to_schemas_lessons(lesson)
            returned_lessons.append(lesson)

        return schemas.lessons.LessonList(
            lessons=returned_lessons
        )

    async def get(
            self, *,
            lesson_schema: LessonCreate
    ) -> tables.Lesson:

        query = select(tables.Lesson).filter_by(
            name=lesson_schema.name,
            start_time=dt.time(**lesson_schema.start_time.dict()),
            end_time=dt.time(**lesson_schema.end_time.dict()),
            weekday=lesson_schema.weekday,
            school_id=lesson_schema.school_id,
            teacher_id=lesson_schema.teacher_id,
            semester_id=lesson_schema.semester_id
        )
        lesson = await self.session.scalar(query)
        if lesson is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return lesson

    async def create(self, lesson_schema: LessonCreate):
        lesson_dct = lesson_schema.dict()
        lesson_dct['start_time'] = dt.time(**lesson_dct['start_time'])
        lesson_dct['end_time'] = dt.time(**lesson_dct['end_time'])
        try:
            new_lesson = tables.Lesson(**lesson_dct)
            self.session.add(new_lesson)
            await self.session.commit()
        except exc.IntegrityError:
            await self.session.rollback()
            new_lesson = await self.get(lesson_schema=lesson_schema)
            self.response.status_code = status.HTTP_200_OK
        return await self._add_teacher(new_lesson)

    async def delete(self,
                     lesson_id: int):
        # TODO: Logic
        return None

    async def add_subgroup_to_lesson(
            self,
            subgroup_lesson: schemas.subgroups_lessons.LessonSubgroupCreate
    ):
        try:
            new_lesson_subgroup = tables.LessonSubgroup(
                **subgroup_lesson.dict()
            )
            self.session.add(new_lesson_subgroup)
            await self.session.commit()
        except exc.IntegrityError:
            self.response.status_code = status.HTTP_200_OK
            return schemas.subgroups_lessons.LessonSubgroup(
                **subgroup_lesson.dict()
            )
        return new_lesson_subgroup
