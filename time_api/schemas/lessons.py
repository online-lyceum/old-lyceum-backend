from typing import Optional

from pydantic import BaseModel, Field

from .times import Time, Date
from .teachers import Teacher


class BaseLesson(BaseModel):
    name: str
    start_time: Time
    end_time: Time
    week: None | bool = None
    weekday: int = Field(0, ge=0, le=6)
    room: str
    school_id: int


class InternalLesson(BaseLesson):
    lesson_id: int

    class Config:
        orm_mode = True


class LessonCreate(BaseLesson):
    teacher_id: int


class Lesson(InternalLesson):
    teacher: Teacher


class DoubleLesson(Lesson):
    start_time: list[Time]
    end_time: list[Time]
    lesson_id: list[int]


class LessonList(BaseModel):
    lessons: list[Lesson]


class LessonListWithDouble(BaseModel):
    lessons: list[DoubleLesson]


class LessonListWithWeekday(BaseModel):
    lessons: list[Lesson]
    weekday: int


class DayLessonList(LessonList):
    is_today: bool
    weekday: None | int
    week: int


class LessonHotfixCreate(BaseModel):
    """Onetime schedule change

    :param is_existing: будет ли урок в этот день"""
    lesson_id: None | int
    name: None | str
    start_time: None | Time
    end_time: None | Time
    room: None | str
    teacher_id: None | int
    is_existing: None | bool = True
    school_id: int | None
    for_date: Date


class LessonHotfix(BaseModel):
    is_existing: bool = True 
    for_date: Date
    hotfix_id: int

    class Config:
        orm_mode = True


