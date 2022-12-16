from fastapi import FastAPI

from time_api import api
from time_api.description import application_metadata
import logging


logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] [%(process)s] [%(levelname)s] "
           "(%(filename)s:%(lineno)d) %(msg)s"
)
logger = logging.getLogger(__name__)
logger.info('Logger start work')


def create_application():
    application = FastAPI(openapi_url='/api/openapi.json',
                          docs_url='/api/docs',
                          redoc_url='/api/redoc',
                          logger=logger,
                          **application_metadata)
    for attribute in filter(lambda x: not x.startswith("_"), dir(api)):
        logger.debug(f'Check {attribute} for router')
        python_module = getattr(api, attribute)
        if hasattr(python_module, 'router'):
            logger.debug(f'Include {attribute} router')
            application.include_router(python_module.router)
    return application


app = create_application()
