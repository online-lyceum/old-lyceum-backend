from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import Time
from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint
from async_lyceum_api.db.base import Base


class Address(Base):
    __tablename__ = "addresses"

    address_id = Column(Integer, autoincrement=True, primary_key=True,
                        index=True)
    city = Column(String)
    place = Column(String)

    __table_args__ = (
        UniqueConstraint('city', 'place', name='uq_city_place'),
    )


class School(Base):
    __tablename__ = "schools"

    school_id = Column(Integer, autoincrement=True, primary_key=True,
                       index=True)
    name = Column(String)
    address_id = Column(ForeignKey('addresses.address_id'))

    __table_args__ = (
        UniqueConstraint('name', 'address_id', name='uq_name_address'),
    )


class ClassType(Base):
    """Тип класса - курс, класс, группа и т.д."""
    __tablename__ = "class_types"
    class_type_id = Column(Integer, autoincrement=True, primary_key=True,
                           index=True)
    name = Column(String, unique=True)


class Class(Base):
    __tablename__ = "classes"

    class_id = Column(Integer, autoincrement=True, primary_key=True,
                      index=True)
    school_id = Column(ForeignKey('schools.school_id', ondelete='CASCADE'))
    number = Column(Integer)
    letter = Column(String)
    class_type_id = Column(ForeignKey('class_types.class_type_id'))

    __table_args__ = (
        UniqueConstraint('school_id', 'number', 'letter', 'class_type_id',
                         name='uq_class'),
    )


class Subgroup(Base):
    """Подгруппы в классе"""
    __tablename__ = "subgroups"

    subgroup_id = Column(Integer, autoincrement=True, primary_key=True,
                         index=True)
    class_id = Column(ForeignKey('classes.class_id', ondelete='CASCADE'))
    name = Column(String)

    __table_args__ = (
        UniqueConstraint('class_id', 'name', name='uq_class_id_name'),
    )


class Teacher(Base):
    __tablename__ = "teachers"

    teacher_id = Column(Integer, autoincrement=True, primary_key=True,
                        index=True)
    name = Column(String)


class Lesson(Base):
    __tablename__ = "lessons"

    lesson_id = Column(Integer, autoincrement=True, primary_key=True,
                       index=True)
    name = Column(String)
    start_time = Column(Time)
    end_time = Column(Time)
    week = Column(Integer)
    weekday = Column(Integer)
    teacher_id = Column(ForeignKey('teachers.teacher_id', ondelete='CASCADE'))
    school_id = Column(ForeignKey('schools.school_id', ondelete='CASCADE'))


class LessonSubgroup(Base):
    """Отношение уроков и подгрупп. У какой подгруппы, какие уроки.
    И какие подгруппы будут на уроке."""
    __tablename__ = "lesson_subgroups"
    lesson_id = Column(
        ForeignKey('lessons.lesson_id', ondelete='CASCADE'),
        primary_key=True
    )
    subgroup_id = Column(
        ForeignKey('subgroups.subgroup_id', ondelete='CASCADE'),
        primary_key=True
    )
