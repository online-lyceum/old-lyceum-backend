from pydantic import BaseModel


class BaseLessonSubgroup(BaseModel):
    subgroup_id: int
    lesson_id: int


class LessonSubgroupCreate(BaseLessonSubgroup):
    pass


class LessonSubgroup(BaseLessonSubgroup):
    class Config:
        orm_mode = True
