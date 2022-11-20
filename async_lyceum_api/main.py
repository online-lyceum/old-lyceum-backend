from fastapi import FastAPI

from async_lyceum_api.handlers import router
from async_lyceum_api.description import application_metadata


def create_application():
    application = FastAPI(**application_metadata)
    application.include_router(router)
    return application


app = create_application()
