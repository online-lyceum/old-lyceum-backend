from pydantic import BaseModel, Field


class Message(BaseModel):
    msg: str


class CityList(BaseModel):
    cities: list[str]


class SchoolWithoutID(BaseModel):
    name: str
    city: str
    place: str


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


class TeacherWithoutID(BaseModel):
    name: str


class Teacher(TeacherWithoutID):
    teacher_id: int


class TeacherList(BaseModel):
    teachers: list[Teacher]


class Time(BaseModel):
    hour: int
    minute: int


class LessonWithoutID(BaseModel):
    name: str
    start_time: Time
    end_time: Time
    week: int
    weekday: int = Field(..., ge=0, le=6)


class LessonWithoutIDWithTeacherID(LessonWithoutID):
    teacher_id: int


class LessonWithoutIDWithTeacher(LessonWithoutID):
    teacher: Teacher


class Lesson(LessonWithoutIDWithTeacher):
    lesson_id: int


class OnlyLessonID(BaseModel):
    lesson_id: int


class LessonOfGroup(OnlyLessonID):
    subgroup_id: int


LessonType = Lesson | LessonOfGroup


class LessonList(BaseModel):
    subgroup_id: int
    lessons: list[Lesson]


class Date(BaseModel):
    weekday: int
    day: int
    month: int


class DayLessonList(LessonList):
    date: Date


class LessonListByClassID(BaseModel):
    class_id: int
    lessons: list[Lesson]


class DaySubgroupLessons(LessonList):
    weekday: int
    week: int
