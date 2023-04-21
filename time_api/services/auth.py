from fastapi import Header, HTTPException
from os import environ


class TokenAuth:
    def __init__(self):
        self.token = environ.get('AUTH_TOKEN', '123456')

    def __call__(self):
        token = self.token

        def _auth(auth_token: str = Header(default='')):
            if auth_token != token:
                raise HTTPException(status_code=401)

        return _auth


authenticate = TokenAuth()
