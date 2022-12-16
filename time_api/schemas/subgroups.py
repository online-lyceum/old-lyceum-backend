from pydantic import BaseModel


class SubgroupWithoutID(BaseModel):
    name: str


class Subgroup(SubgroupWithoutID):
    subgroup_id: int


class SubgroupInfo(BaseModel):
    subgroup_id: int
    subgroup_name: str
    class_id: int
    class_number: int
    class_letter: str
    school_id: int
    school_name: str


class SubgroupList(BaseModel):
    class_id: int
    subgroups: list[Subgroup]
