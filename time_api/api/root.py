import logging

from fastapi import APIRouter

from time_api import schemas


logger = logging.getLogger(__name__)
router = APIRouter(
    prefix='/api',
    tags=["Hello"],
)


@router.get('', response_model=schemas.messages.Message)
async def get_hello_msg():
    return schemas.messages.Message(msg='Hello from FastAPI and Lawrence')
