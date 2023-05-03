from pydantic import BaseModel


class Token(BaseModel):
    key: str


class User(BaseModel):
    name: str
    password: str


class UserCreate(User):
    """
    :param access_level: 1 for Monitor, 2 for Teacher, 3 for Admin"""
    access_level: int = 0
