import logging

from fastapi import APIRouter, Depends, UploadFile

from time_api import schemas
from time_api.services.auth import authenticate
from time_api.services.parser import get_lessons_list, get_timetable_data
from time_api.services.parser import TimetableService
from time_api.services.classes import ClassService
from time_api.services.subgroups import SubgroupService


logger = logging.getLogger(__name__)
router = APIRouter(
    prefix='/api/timetable',
    tags=['Lessons parse'],
)


@router.post(
    '',
    status_code=201
)
async def create_lessons(
        lessons_file: UploadFile,
        school_id: int,
        _=Depends(authenticate.teacher()),
        service=Depends(TimetableService),
        class_service=Depends(ClassService),
        subgroup_service=Depends(SubgroupService)
):
    lessons_file = lessons_file.file.read()
    data = get_timetable_data(lessons_file)
    for class_number in data['class_numbers']:
        for class_letter in data['class_letters']:
            class_id = (await class_service.create(schemas.classes.ClassCreate(
                number=int(class_number),
                letter=class_letter,
                school_id=school_id
            ))).class_id
            for subgroup_name in data['subgroup_names']:
                s = await subgroup_service.create(schemas.subgroups.SubgroupCreate(
                        name=subgroup_name,
                        class_id=class_id
                ))
    lessons_list = get_lessons_list(lessons_file)
    return await service.create(lessons_list, school_id)


@router.patch(
    '',
    status_code=201
)
async def hotfix_lesons(
        lessons_file: UploadFile,
        school_id: int,
        _=Depends(authenticate.teacher()),
        service=Depends(TimetableService),
):
    lessons_file = lessons_file.file.read()
    lessons_list = get_lessons_list(lessons_file)
    return await service.hotfix(lessons_list, school_id)
