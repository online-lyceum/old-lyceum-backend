FROM python:3.11-slim
WORKDIR /app
COPY ./dist/*.whl /wheels/
RUN pip3 install /wheels/*
CMD async_lyceum_api -H $POSTGRES_HOST -S $POSTGRES_PASSWORD
