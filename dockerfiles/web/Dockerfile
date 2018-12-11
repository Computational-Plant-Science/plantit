#
# Django webserver
#

FROM python:3
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install -y erlang rabbitmq-server python3-numpy-dev
RUN apt-get autoclean

RUN mkdir /code
WORKDIR /code
COPY ./requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
