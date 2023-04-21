import logging
from typing import Optional

from fastapi import APIRouter, Depends

from time_api import schemas
from time_api.services.classes import ClassService
from time_api.services.auth import authenticate


logger = logging.getLogger(__name__)
router = APIRouter(
    prefix='/api/auth',
    tags=['Authentication'],
)


@router.post(
    '',
    response_model=schemas.classes.ClassList
)
def register():
    # TODO: Create user register
    pass


# TODO: Create user login


# TODO: Refresh token