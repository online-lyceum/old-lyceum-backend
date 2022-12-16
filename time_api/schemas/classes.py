from pydantic import BaseModel


class BaseClass(BaseModel):
    number: int
    letter: str


class ClassCreate(BaseClass):
    school_id: int


class Class(BaseClass):
    class_id: int

    class Config:
        orm_mode = True


class ClassList(BaseModel):
    school_id: int
    classes: list[Class]
