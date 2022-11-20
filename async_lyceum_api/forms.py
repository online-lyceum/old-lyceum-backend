from pydantic import BaseModel


class Message(BaseModel):
    msg: str


class SchoolWithoutID(BaseModel):
    name: str
    address: str


class School(SchoolWithoutID):
    school_id: int


class SchoolList(BaseModel):
    schools: list[School]


class ClassWithoutID(BaseModel):
    number: int
    letter: str
    class_type: str = "класс"


class Class(ClassWithoutID):
    class_id: int


class ClassList(BaseModel):
    school_id: int
    classes: list[Class]


class SubgroupWithoutID(BaseModel):
    name: str


class Subgroup(SubgroupWithoutID):
    subgroup_id: int


class SubgroupList(BaseModel):
    class_id: int
    subgroups: list[Subgroup]


class TeacherWithoutID(BaseModel):
    name: str


class Teacher(TeacherWithoutID):
    teacher_id: int


class TeacherList(BaseModel):
    teachers: list[Teacher]
