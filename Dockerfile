FROM python:3.11
WORKDIR /app
COPY requirements.txt ./
RUN pip3 install -r requirements.txt
COPY setup.py ./
COPY ./async_lyceum_api ./async_lyceum_api
RUN pip3 install .
CMD gunicorn async_lyceum_api.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:80
