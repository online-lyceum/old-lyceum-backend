from pydantic import BaseModel


class Token(BaseModel):
    key: str


class User(BaseModel):
    name: str
    password: str


class UserCreate(User):
    """
    :param access_level: 1 for Class president, 2 for Teacher, 3 for Admin
    :param teacher_id: Only for access_level=2
    :param class_id: Only for access_level=1"""
    access_level: int = 0
    teacher_id: int | None
    class_id: int | None


class UserInfo(BaseModel):
    teacher_id: int | None
    access_level: int = 0
    class_id: int | None
    name: str
    token: Token | None

    class Config:
        orm_mode = True

