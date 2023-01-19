from fastapi import FastAPI

import logging


logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] [%(process)s] [%(levelname)s] "
           "(%(filename)s:%(lineno)d) %(msg)s"
)
logger = logging.getLogger("time_api")
logger.setLevel("DEBUG")
logger.info('Logger start work')

from time_api import api
from time_api.description import application_metadata


def create_application():
    application = FastAPI(openapi_url='/api/openapi.json',
                          docs_url='/api/docs',
                          redoc_url='/api/redoc',
                          logger=logger,
                          **application_metadata)
    application.include_router(api.root.router)
    application.include_router(api.schools.router)
    application.include_router(api.classes.router)
    application.include_router(api.subgroups.router)
    application.include_router(api.teachers.router)
    application.include_router(api.semesters.router)
    application.include_router(api.lessons.router)
    return application


app = create_application()
