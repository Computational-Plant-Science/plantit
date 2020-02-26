FROM python:3
ENV PYTHONUNBUFFERED 1

RUN apt-get -y update \
    && apt-get install -y erlang rabbitmq-server python3-numpy-dev \
    && apt-get install -y postgresql-client \
    && apt-get autoclean

RUN mkdir /code
WORKDIR /code
COPY ./requirements.txt /code/
COPY ./wait-for-postgres.sh /code/
RUN chmod +x wait-for-postgres.sh
RUN pip install -r requirements.txt
COPY . /code/
