from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import Time
from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy import Date
from .base import Base


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, autoincrement=True, primary_key=True,
                       index=True)
    name = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    access_level = Column(Integer, nullable=False, default=0)


class School(Base):
    __tablename__ = "schools"

    school_id = Column(Integer, autoincrement=True, primary_key=True,
                       index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    is_using_double_week = Column(Boolean)

    __table_args__ = (
        UniqueConstraint('name', 'address', name='uq_name_address'),
    )


class Class(Base):
    __tablename__ = "classes"

    class_id = Column(Integer, autoincrement=True, primary_key=True,
                      index=True)
    school_id = Column(ForeignKey('schools.school_id', ondelete='CASCADE'))
    number = Column(Integer)
    letter = Column(String)

    __table_args__ = (
        UniqueConstraint('school_id', 'number', 'letter'),
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
    name = Column(String, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    week = Column(Integer)
    weekday = Column(Integer, nullable=False)
    room = Column(String, nullable=False)
    teacher_id = Column(ForeignKey('teachers.teacher_id', ondelete='CASCADE'),
                        nullable=False)
    school_id = Column(ForeignKey('schools.school_id', ondelete='CASCADE'),
                       nullable=False)

    __table_args__ = (
        UniqueConstraint(
            'name',
            'start_time',
            'end_time',
            'weekday',
            'room',
            'school_id',
            'teacher_id'
        ),
    )


class LessonSubgroup(Base):
    """Отношение уроков и подгрупп. У какой подгруппы, какие уроки.
    И какие подгруппы будут на уроке."""
    __tablename__ = "lesson_subgroups"
    lesson_id = Column(
        ForeignKey('lessons.lesson_id', ondelete='RESTRICT'),
        primary_key=True
    )
    subgroup_id = Column(
        ForeignKey('subgroups.subgroup_id', ondelete='RESTRICT'),
        primary_key=True
    )


class Semester(Base):
    """Время от каникул до каникул.
    week_reverse - отвечает за порядок недель.
    Неделя верхняя если (week_num + week_reverse) % 2 == 0"""
    __tablename__ = "semesters"
    semester_id = Column(Integer, autoincrement=True, primary_key=True,
                         index=True)
    school_id = Column(ForeignKey('schools.school_id',
                                  ondelete='CASCADE'), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    week_reverse = Column(Boolean, nullable=True, default=None)

    __table_args__ = (
        UniqueConstraint(
            'school_id',
            'start_date',
            'end_date'
        ),
    )
