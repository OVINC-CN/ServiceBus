FROM python:3.10
RUN mkdir -p /usr/src/service-bus/logs /usr/src/service-bus/celery-logs
COPY . /usr/src/service-bus
WORKDIR /usr/src/service-bus
RUN pip install -U pip && pip install -r requirements.txt -i https://mirrors.cloud.tencent.com/pypi/simple
