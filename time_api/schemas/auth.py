from pydantic import BaseModel


class Token(BaseModel):
    key: str


class User(BaseModel):
    """
    :param access_level: 1 for Monitor, 2 for Teacher, 3 for Admin"""
    name: str
    password: str
    access_level: int = 0
