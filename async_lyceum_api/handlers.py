from async_lyceum_api.db import db_manager
from async_lyceum_api.db.base import get_session
from async_lyceum_api.forms import *

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()


@router.get('/', response_model=Message)
async def get_hello_msg():
    return Message(msg='Hello from FastAPI and Lawrence')


@router.get('/school', response_model=SchoolList)
async def get_schools(session: AsyncSession = Depends(get_session)):
    res = await db_manager.get_school_list(session)
    schools = []
    for x in res:
        schools.append(
            SchoolWithId(
                school_id=x.school_id,
                name=x.name,
                address=x.address
            )
        )
    return SchoolList(schools=schools)


@router.post('/school', response_model=SchoolWithId)
async def create_school(school: School,
                        session: AsyncSession = Depends(get_session)):
    new_school = await db_manager.add_school(session, **dict(school))
    return SchoolWithId(
        school_id=new_school.school_id,
        name=new_school.name,
        address=new_school.address
    )


@router.get('/school/{school_id}/class')
async def get_classes(school_id: int):
    return {'school_id': school_id, 'classes': []}


@router.get('/teacher')
async def get_teachers():
    return {'teachers': []}
