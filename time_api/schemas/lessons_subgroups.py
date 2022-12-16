from pydantic import BaseModel


class BaseLessonSubgroup(BaseModel):
    lesson_id: int


class LessonSubgroupCreate(BaseLessonSubgroup):
    pass


class LessonOfGroup(BaseLessonSubgroup):
    subgroup_id: int
