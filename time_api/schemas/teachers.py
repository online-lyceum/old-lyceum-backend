from pydantic import BaseModel


class BaseTeacher(BaseModel):
    name: str


class TeacherCreate(BaseTeacher):
    pass


class Teacher(BaseTeacher):
    teacher_id: int

    class Config:
        orm_mode = True


class TeacherList(BaseModel):
    teachers: list[Teacher]
