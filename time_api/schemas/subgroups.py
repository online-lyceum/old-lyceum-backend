from pydantic import BaseModel


class BaseSubgroup(BaseModel):
    name: str
    class_id: int = None


class SubgroupCreate(BaseSubgroup):
    class_id: int


class Subgroup(BaseSubgroup):
    subgroup_id: int

    class Config:
        orm_mode = True


class SubgroupInfo(BaseModel):
    subgroup_id: int
    subgroup_name: str
    class_id: int
    class_number: int
    class_letter: str
    school_id: int
    school_name: str


class SubgroupList(BaseModel):
    subgroups: list[Subgroup]
