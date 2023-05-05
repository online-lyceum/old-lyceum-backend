import logging
import datetime as dt
from typing import Optional, Any
from itertools import groupby

from sqlalchemy import select, exc
from fastapi import status, HTTPException

from time_api.services.base import BaseService
from time_api.db import tables
from time_api.schemas.lessons import LessonCreate, Lesson
from time_api import schemas
from time_api.services.teachers import TeacherService
from time_api.services.semesters import SemesterService
from time_api.services.lessons_hotfix import LessonHotfixService

logger = logging.getLogger(__name__)


class LessonService(BaseService):

    async def get_list(
            self,
            class_id: Optional[int] = None,
            subgroup_id: Optional[int] = None,
            week: Optional[bool] = None,
            weekday: Optional[int | list[int]] = None,
            do_double: bool = False,
            group_by_weekdays: Optional[bool] = None,
            teacher_id: int | None = None
    ) -> schemas.lessons.LessonList | schemas.lessons.LessonListWithDouble:
        semester_service = SemesterService(self.session, self.response)
        try:
            await semester_service.get_current()
        except HTTPException as e:
            if e.status_code == 404:
                return schemas.lessons.LessonList(lessons=[])
            else:
                raise e

        lessons = await self._get_list(
            class_id=class_id,
            subgroup_id=subgroup_id,
            week=week,
            weekday=weekday,
            teacher_id=teacher_id
        )
        lessons = [await self._add_teacher(lesson) for lesson in lessons]

        if group_by_weekdays:
            lessons.sort(key=lambda i: i['weekday'])

            lessons_with_weekdays = [
                (weekday, list(lessons)) for weekday, lessons in
                groupby(lessons, lambda lesson: lesson['weekday'])
            ]
            lessons_with_weekdays.sort(key=lambda x: x[0])
            lessons = [lesson for _, lesson in lessons_with_weekdays]

        if do_double and lessons:  # Check for double lesson
            if isinstance(lessons[0], list):
                return [schemas.lessons.LessonListWithDouble(
                            lessons=self._double_lessons(group)
                        ) for group in lessons]
            return schemas.lessons.LessonListWithDouble(
                lessons=self._double_lessons(lessons)
            )

        if lessons and isinstance(lessons[0], list):
            return [schemas.lessons.LessonList(lessons=group) for group in lessons]
        return schemas.lessons.LessonList(
            lessons=lessons
        )

    def _double_lessons(
            self,
            lessons: list
    ) -> list[schemas.lessons.DoubleLesson]:
        if any([isinstance(lesson, schemas.lessons.Lesson) for lesson in lessons]):
            lessons = [dict(lesson) for lesson in lessons]
        checked_indexes = []
        for i in range(len(lessons)):
            if i in checked_indexes:
                continue
            if i < len(lessons) - 1 \
                    and lessons[i]['name'] == lessons[i + 1]['name'] \
                    and lessons[i].get('teacher_id') == lessons[i + 1].get('teacher_id') \
                    and lessons[i]['room'] == lessons[i + 1]['room']:
                lessons[i]['start_time'] = [
                    lessons[i]['start_time'],
                    lessons[i + 1]['start_time']
                ]
                lessons[i]['end_time'] = [
                    lessons[i]['end_time'],
                    lessons[i + 1]['end_time']
                ]
                lessons[i]['lesson_id'] = [
                        lessons[i]['lesson_id'], 
                        lessons[i + 1]['lesson_id']
                ]
                checked_indexes.append(i + 1)
            else:
                lessons[i]['start_time'] = [lessons[i]['start_time']]
                lessons[i]['end_time'] = [lessons[i]['end_time']]
                lessons[i]['lesson_id'] = [lessons[i]['lesson_id']]
        for i in sorted(checked_indexes, reverse=True):
            del lessons[i]
        return lessons 

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
            week: Optional[bool] = None,
            weekday: Optional[int | list[int]] = None,
            teacher_id: int | None = None
    ) -> list[tables.Lesson] | list[list[tables.Lesson]]:

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

        if week is not None:
            query = query.filter(
                tables.Lesson.week == week
            )

        if weekday is not None:
            if isinstance(weekday, int):
                query = query.filter(
                    tables.Lesson.weekday == weekday
                )

        if teacher_id is not None:
            query = query.filter_by(teacher_id=teacher_id)

        query = query.order_by(tables.Lesson.start_time)

        lessons = list(await self.session.scalars(query))

        if not lessons:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        return lessons

    async def get_weekday_list(
            self,
            weekday: Optional[int] = None,
            class_id: Optional[int] = None,
            subgroup_id: Optional[int] = None
    ) -> schemas.lessons.LessonList:
        lessons = await self._get_list(class_id=class_id,
                                       subgroup_id=subgroup_id,
                                       weekday=weekday)
        lessons = [await self._add_teacher(lesson) for lesson in lessons]
        logger.debug(f'Today has {lessons=}')
        returned_lessons: list[Lesson] = []
        for lesson in lessons:
            schemas_lesson = Lesson(
                name=lesson['name'],
                start_time=dt.time(**lesson['start_time']),
                end_time=dt.time(**lesson['end_time']),
                week=lesson['week'],
                weekday=lesson['weekday'],
                room=lesson['room'],
                school_id=lesson['school_id'],
                lesson_id=lesson['lesson_id'],
                teacher=schemas.teachers.Teacher(
                    **schemas.teachers.Teacher.from_orm(
                        lesson['teacher']).dict()
                )
            )
            returned_lessons.append(schemas_lesson)

        return schemas.lessons.LessonList(
            lessons=returned_lessons
        )

    async def is_using_double_week(
            self,
            class_id: int | None = None,
            subgroup_id: int | None = None
    ) -> bool:
        query = select(tables.School.is_using_double_week).join(tables.Class)
        if class_id is not None:
            query.filter_by(class_id=class_id)

        if subgroup_id is not None:
            query = query.join(tables.Subgroup)
            query = query.filter_by(subgroup_id=subgroup_id)

        return await self.session.scalar(query)

    async def get_today_list(
            self,
            class_id: Optional[int] = None,
            subgroup_id: Optional[int] = None
    ) -> schemas.lessons.LessonList:
        logger.info(f'Current time is {dt.datetime.now()}')
        today = dt.datetime.today().weekday()
        is_using_double_week = await self.is_using_double_week(
            class_id, subgroup_id
        )
        week_range = 7 + 7 * is_using_double_week
        for day in range(week_range):
            lessons = await self.get_weekday_list(
                weekday=(today + day) % week_range,
                class_id=class_id,
                subgroup_id=subgroup_id
            )
            last_end_time = dt.time(**lessons.lessons[-1].end_time.dict())
            is_ended = last_end_time < dt.datetime.now().time() and not day
            if lessons and not is_ended:
                return lessons
        return schemas.lessons.LessonList(lessons=[])

    async def get_weekday_list_with_weekday(
            self,
            weekday: int,
            class_id: Optional[int] = None,
            subgroup_id: Optional[int] = None
    ) -> schemas.lessons.LessonListWithWeekday:
        lessons = await self.get_weekday_list(class_id=class_id,
                                              subgroup_id=subgroup_id,
                                              weekday=weekday)
        return schemas.lessons.LessonListWithWeekday(
            lessons=lessons.lessons,
            weekday=weekday
        )

    async def get_nearest_list(
            self,
            class_id: Optional[int] = None,
            subgroup_id: Optional[int] = None,
            teacher_id: int | None = None,
            do_double: bool = False,
            weekday: int = None
    ) -> schemas.lessons.LessonList | schemas.lessons.LessonListWithDouble:
        if weekday is None:
            weekday = dt.datetime.today().weekday()
        nearest_lessons = await self.get_list(
            class_id=class_id,
            subgroup_id=subgroup_id,
            group_by_weekdays=True,
            teacher_id=teacher_id
        )
        nearest_lessons = list(filter(lambda i: i.lessons and i.lessons[0].weekday >= weekday, 
                                      nearest_lessons)) + \
                          list(filter(lambda i: i.lessons and i.lessons[0].weekday < weekday,
                                      nearest_lessons))
        ret = None
        for group in nearest_lessons:
            if group.lessons:
                if weekday == group.lessons[0].weekday:
                    end_time = group.lessons[-1].end_time
                    if end_time.hour < dt.datetime.now().hour \
                            or end_time.hour == dt.datetime.now().hour \
                            and end_time.minute < dt.datetime.now().minute:
                        continue
                ret = group
                break

        if ret is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        hotfix_service = LessonHotfixService(self.session, self.response)
        lessons_weekday = ret.lessons[0].weekday
        ret = await hotfix_service.hotfix_lessons(ret)
        if not ret.lessons:
            return await self.get_nearest_list(class_id, subgroup_id, do_double, lessons_weekday + 1)
        if do_double:
            ret = schemas.lessons.LessonListWithDouble(lessons=self._double_lessons(ret.lessons))
        return ret

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
            teacher_id=lesson_schema.teacher_id
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


