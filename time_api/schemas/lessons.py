from typing import Optional

from pydantic import BaseModel, Field

from .times import Time, Date
from .teachers import Teacher


class BaseLesson(BaseModel):
    name: str
    start_time: Time
    end_time: Time
    week: Optional[bool] = None
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


class LessonList(BaseModel):
    lessons: list[Lesson]


class LessonListWithDouble(BaseModel):
    lessons: list[DoubleLesson]


class LessonListWithWeekday(BaseModel):
    lessons: list[Lesson]
    weekday: int


class DayLessonList(LessonList):
    is_today: bool
    weekday: Optional[int]
    week: int


class LessonHotfix(BaseModel):
    """Onetime schedule change

    :param is_existing: будет ли урок в этот день"""
    lesson_id: int
    name: Optional[str]
    start_time: Optional[Time]
    end_time: Optional[Time]
    room: Optional[str]
    teacher_id: Optional[int]
    is_existing: Optional[bool] = True 
    for_date: Date

