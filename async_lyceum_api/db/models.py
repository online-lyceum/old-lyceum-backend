from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from async_lyceum_api.db.base import Base


class School(Base):
    __tablename__ = "schools"

    school_id = Column(Integer, autoincrement=True, primary_key=True,
                       index=True)
    name = Column(String, unique=True)
    address = Column(String)


class ClassType(Base):
    __tablename__ = "class_types"
    class_type_id = Column(Integer, autoincrement=True, primary_key=True,
                           index=True)
    name = Column(String)


class Class(Base):
    __tablename__ = "classes"

    class_id = Column(Integer, autoincrement=True, primary_key=True,
                      index=True)
    school_id = Column(ForeignKey('schools.school_id'))
    number = Column(Integer)
    letter = Column(String)
    class_type_id = Column(ForeignKey('class_types.class_type_id'))


class Subgroup(Base):
    __tablename__ = "subgroups"

    subgroup_id = Column(Integer, autoincrement=True, primary_key=True,
                         index=True)
    class_id = Column(ForeignKey('classes.class_id'))
    name = Column(String)


class Teacher(Base):
    __tablename__ = "teachers"

    teacher_id = Column(Integer, autoincrement=True, primary_key=True,
                       index=True)
    name = Column(String)
