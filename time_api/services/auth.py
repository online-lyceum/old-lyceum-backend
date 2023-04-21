from fastapi import Header, HTTPException
from os import environ


class User:
    pass


class TokenAuth:
    def __init__(self):
        self.token = environ.get('AUTH_TOKEN', '123456')
        # TODO: redis connection

    def __call__(self):
        token = self.token

        def _auth(auth_token: str = Header(default='')):
            # TODO: Get from redis
            if auth_token != token:
                raise HTTPException(status_code=401)

        return _auth

    # TODO: Auth level


authenticate = TokenAuth()
