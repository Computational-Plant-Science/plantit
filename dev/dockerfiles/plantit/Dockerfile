FROM python:3
ENV PYTHONUNBUFFERED 1

RUN apt-get -y update \
    && apt-get install -y erlang rabbitmq-server python3-numpy-dev \
    && apt-get install -y postgresql-client \
    && apt-get autoclean

RUN mkdir /code
WORKDIR /code
COPY ./dockerfiles/plantit/requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/

