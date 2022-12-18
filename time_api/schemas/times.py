from pydantic import BaseModel


class Time(BaseModel):
    hour: int
    minute: int

    class Config:
        orm_mode = True


class Date(BaseModel):
    day: int
    month: int
    year: int

    class Config:
        orm_mode = True