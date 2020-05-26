FROM python:3.6-buster
ENV PYTHONUNBUFFERED 1

RUN apt-get -y update \
    && apt-get install -y erlang rabbitmq-server python3-numpy-dev \
    && apt-get install -y postgresql-client \
    && apt-get install -yqq cron \
    && apt-get install -y openssh-client \
    && apt-get install -y sshpass \
    && apt-get install -y curl vim \
    && apt-get autoclean

RUN mkdir /code
WORKDIR /code
COPY . ./
RUN pip install -r dev/dockerfiles/plantit/requirements.txt
RUN chmod +x dev/configure-irods.sh
RUN chmod +x dev/configure-superuser.sh
RUN chmod +x dev/start-dagit.sh
RUN chmod +x dev/wait-for-it.sh
RUN chmod +x dev/wait-for-postgres.sh
RUN chmod +x dev/create-dagster-databases.sh
RUN chmod +x dev/ssh-echo-pass.sh


