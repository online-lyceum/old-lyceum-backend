from typing import Optional

from pydantic import BaseModel, Field

from .times import Time
from .teachers import Teacher


class BaseLesson(BaseModel):
    name: str
    start_time: Time
    end_time: Time
    week: Optional[bool] = None
    weekday: int = Field(0, ge=0, le=6)
    school_id: int


class LessonCreate(BaseLesson):
    teacher_id: int


class Lesson(BaseLesson):
    lesson_id: BaseLesson
    teacher: Teacher

    class Config:
        orm_mode = True


class LessonList(BaseModel):
    lessons: list[Lesson]


class DayLessonList(LessonList):
    weekday: int
    week: int
