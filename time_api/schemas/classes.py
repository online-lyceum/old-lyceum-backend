from typing import Optional

from pydantic import BaseModel

from .subgroups import Subgroup


class BaseClass(BaseModel):
    number: int
    letter: str
    school_id: int


class ClassCreate(BaseClass):
    pass


class Class(BaseClass):
    class_id: int

    class Config:
        orm_mode = True


class ClassList(BaseModel):
    classes: list[Class]
