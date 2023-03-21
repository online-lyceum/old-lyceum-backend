from pydantic import BaseModel


class BaseSchool(BaseModel):
    name: str
    address: str
    is_using_double_week: bool


class SchoolCreate(BaseSchool):
    pass


class School(BaseSchool):
    school_id: int

    class Config:
        orm_mode = True


class SchoolList(BaseModel):
    schools: list[School]
