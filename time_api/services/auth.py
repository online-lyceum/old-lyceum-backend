from fastapi import Header, HTTPException
from os import environ
from redis import Redis
from uuid import uuid4
from enum import IntEnum

from loguru import logger

from sqlalchemy import select, exc

from .base import BaseService
from time_api import schemas
from time_api.db import tables


class AccessLevel(IntEnum):
    admin = 3
    teacher = 2
    class_president = 1
    unauthorized = 0


class UserService(BaseService):
    async def create(
            self,
            user_schema: schemas.auth.UserCreate
    ):
        user_schema = user_schema.dict()
        if 'token' in user_schema.keys():
            user_schema.pop('token')
        new_user = tables.User(**user_schema)
        try:
            self.session.add(new_user)
            await self.session.commit()
        except exc.IntegrityError:
            raise HTTPException(status_code=409)
        return new_user

    async def get(self, name: str):
        query = select(tables.User)
        query = query.filter_by(name=name)

        user = await self.session.scalar(query)
        if user is None:
            raise HTTPException(status_code=404)
        return user


class TokenAuth:
    EXPIRE_TIME = 3 * 24 * 60 * 60
    def __init__(self, *args, **kwargs):
        self.connection = Redis(*args, **kwargs)
        if environ.get('ADMIN_TOKEN') and environ.get('ADMIN_PASSWORD'):
            logger.debug("Create admin account")
            self.connection.hset(environ.get('ADMIN_TOKEN'),
                    mapping={"name": "admin", "password": environ.get('ADMIN_PASSWORD'),
                             "access_level": AccessLevel.admin.value})

    def create_token(self, name: str, password: str, 
                    access_level: int = AccessLevel.unauthorized.value):
        if isinstance(access_level, str) and access_level.isdigit():
            access_level = int(access_level)
        if access_level not in range(min(AccessLevel), max(AccessLevel) + 1):
            raise ValueError("invalid access_level")
        token_key = str(uuid4())
        with self.connection.pipeline() as pipeline:
            pipeline = pipeline.hset(token_key, 
                    mapping={"name": name, "password": password, "access_level": access_level})
            pipeline = pipeline.expire(token_key, self.EXPIRE_TIME)
            res = pipeline.execute()
        return token_key

    def refresh_token(self, token_key: str) -> str:
        return self.create_token(**self.connection.hgetall(token_key))

    def token_exists(self, token_key: str) -> bool:
        return self.connection.exists(token_key)

    def get_info_by_token(self, token_key: str) -> dict:
        return self.connection.hgetall(token_key)

    def __call__(self, access_level=AccessLevel.unauthorized):
        connection = self.connection

        def _auth(auth_token: str = Header(default='')) -> dict:
            if not self.token_exists(auth_token):
                raise HTTPException(status_code=401)
            user_access_level = connection.hget(auth_token, 'access_level')
            if int(user_access_level) < access_level.value:
                raise HTTPException(status_code=401)
            return dict(
                    [((k, v) if not v.isdigit() else (k, int(v)))
                        for k, v in connection.hgetall(auth_token).items()
                    ]
            )

        return _auth

    def admin(self):
        return self(AccessLevel.admin)

    def teacher(self):
        return self(AccessLevel.teacher)

    def class_president(self):
        return self(AccessLevel.class_president)


authenticate = TokenAuth(host='redis', charset="utf-8", decode_responses=True)
