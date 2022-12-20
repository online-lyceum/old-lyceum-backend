from typing import Optional

from pydantic import BaseModel
from .times import Date


class BaseSemester(BaseModel):
    school_id: int
    start_date: Date
    end_date: Date
    week_reverse: Optional[bool] = None


class SemesterCreate(BaseSemester):
    pass


class Semester(BaseSemester):
    semester_id: int

    class Config:
        orm_mode = True


class SemesterList(BaseModel):
    semesters: list[Semester]


class CurrentSemester(BaseModel):
    week: Optional[bool]
    semester: Semester
