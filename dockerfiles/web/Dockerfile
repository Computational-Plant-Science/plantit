#
# Django webserver
#

FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY ./requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/

RUN apt-get update
RUN apt-get install -y erlang rabbitmq-server
RUN apt-get autoclean
