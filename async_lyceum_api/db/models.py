from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from async_lyceum_api.db.base import Base


class School(Base):
    __tablename__ = "schools"

    school_id = Column(Integer, autoincrement=True, primary_key=True,
                       index=True)
    name = Column(String, unique=True)
    address = Column(String)
