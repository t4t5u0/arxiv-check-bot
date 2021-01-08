FROM python:3.9

RUN mkdir /app

WORKDIR /app

ADD . /app

RUN pip install -U pip
RUN pip install --trusted-host pypi.python.org -r requirements.txt