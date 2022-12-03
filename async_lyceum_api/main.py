from fastapi import FastAPI

from async_lyceum_api.handlers import router
from async_lyceum_api.description import application_metadata
import logging


logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s] [%(process)s] [%(levelname)s] (%(filename)s:%(lineno)d) %(msg)s")
logger = logging.getLogger("lyceum")
logger.info('Logger start work')


def create_application():
    application = FastAPI(openapi_url='/api/openapi.json',
                          docs_url='/api/docs',
                          redoc_url='/api/redoc',
                          logger=logger,
                          **application_metadata)
    application.include_router(router)
    return application


app = create_application()
