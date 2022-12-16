from pydantic import BaseModel


class Time(BaseModel):
    hour: int
    minute: int
