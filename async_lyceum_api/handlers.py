from async_lyceum_api.models import *
from fastapi import APIRouter


router = APIRouter()


@router.get('/', response_model=Message)
async def get_hello_msg():
    return Message(msg='message')


@router.get('/school', response_model=SchoolList)
async def get_schools():
    return SchoolList(schools=[])


@router.post('/school', response_model=SchoolWithId)
async def create_school(_: School):
    return School(school_id=1, name='Lyceum 2', address='Irkutsk')


@router.get('/school/{school_id}/class')
async def get_classes(school_id: int):
    return {'school_id': school_id, 'classes': []}


@router.get('/teacher')
async def get_teachers():
    return {'teachers': []}
