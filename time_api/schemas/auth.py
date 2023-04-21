from pydantic import BaseModel


class Token(BaseModel):
    key: str


class User(BaseModel):
    name: str
    password: str


class CreateUser(User):
    access_level: int
