from pydantic import BaseModel, Field

from .times import Time
from .teachers import Teacher


class BaseLesson(BaseModel):
    name: str
    start_time: Time
    end_time: Time
    week: int
    weekday: int = Field(..., ge=0, le=6)


class LessonCreate(BaseLesson):
    teacher_id: int


class Lesson(BaseLesson):
    lesson_id: BaseLesson
    teacher: Teacher

    class Config:
        orm_mode = True


class BaseLessonList(BaseModel):
    lessons: list[Lesson]

    class Config:
        orm_mode = True


class LessonListBySubgroupID(BaseLessonList):
    subgroup_id: int


class LessonListByClassID(BaseLessonList):
    class_id: int


class DayLessonListByClassID(LessonListBySubgroupID):
    weekday: int
    week: int


class DayLessonListBySubgroupID(LessonListByClassID):
    weekday: int
    week: int
