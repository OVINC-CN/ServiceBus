FROM python:3.10
RUN mkdir -p /usr/src/service-bus/logs /usr/src/service-bus/celery-logs
COPY . /usr/src/service-bus
WORKDIR /usr/src/service-bus
RUN apt-get update && apt-get install python-dev python3-dev gcc -y
RUN pip3 install -U pip && pip3 install -r requirements.txt -i https://mirrors.cloud.tencent.com/pypi/simple
