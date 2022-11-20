from pydantic import BaseModel


class Message(BaseModel):
    msg: str


class School(BaseModel):
    name: str
    address: str


class SchoolWithId(School):
    school_id: int


class SchoolList(BaseModel):
    schools: list[SchoolWithId]
