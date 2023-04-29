import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends

from time_api import schemas
from time_api.services.classes import ClassService
from time_api.services.auth import authenticate, UserService


logger = logging.getLogger(__name__)
router = APIRouter(
    prefix='/api/auth',
    tags=['Authentication'],
)


@router.post(
    '/register',
    response_model=schemas.auth.Token
)
async def register(
        user: schemas.auth.User,
        auth_data=Depends(authenticate.teacher()),
        user_service: UserService = Depends(UserService) ):
    if auth_data.get('access_level', 0) < user.access_level:
        raise HTTPException(status_code=401)
    await user_service.create(user_schema=user)
    return schemas.auth.Token(
            key=authenticate.create_token(**user.dict())
        )


@router.post(
    '/login',
    response_model=schemas.auth.Token
)
async def login(user: schemas.auth.User, user_service=Depends(UserService)):
    user_data = await user_service.get(name=user.name)
    if user_data.password == user.password:
        return schemas.auth.Token(
                key=authenticate.create_token(name=user.name, password=user.password)
        )
    raise HTTPException(status_code=401)


@router.put(
    '/refresh',
    response_model=schemas.auth.Token
)
async def refresh(token: schemas.auth.Token):
    return schemas.auth.Token(
            key=authenticate.refresh_token(token_key=token.key)
    )

