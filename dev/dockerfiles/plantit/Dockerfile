FROM python:3.6-buster
ENV PYTHONUNBUFFERED 1

RUN apt-get -y update \
    && apt-get install -y erlang rabbitmq-server python3-numpy-dev \
    && apt-get install -y postgresql-client \
    && apt-get install -yqq cron \
    && apt-get autoclean

RUN mkdir /code
WORKDIR /code
COPY ./dockerfiles/plantit/requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
RUN chmod +x /code/configure-irods.sh
RUN chmod +x /code/configure-superuser.sh
RUN chmod +x /code/start-dagit.sh
RUN chmod +x /code/wait-for-it.sh
RUN chmod +x /code/wait-for-postgres.sh

