FROM python:3.11
WORKDIR /app
COPY requirements_dev.txt ./
RUN pip3 install -r requirements_dev.txt
COPY requirements.txt ./
RUN pip3 install -r requirements.txt
COPY setup.py ./
COPY ./async_lyceum_api ./async_lyceum_api
RUN pip3 install .
CMD uvicorn async_lyceum_api.main:app --port=80 --host='0.0.0.0'
