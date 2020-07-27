FROM python:3.6-buster
ENV PYTHONUNBUFFERED 1

RUN apt-get -y update && apt-get install -y \
    python3-numpy-dev \
    cron \
    openssh-client \
    sshpass \
    curl \
    vim \
    expect

RUN mkdir /code
WORKDIR /code
COPY . ./
RUN pip install -r dev/dockerfiles/plantit/requirements.txt
RUN chmod +x dev/configure-irods.sh
RUN chmod +x dev/configure-superuser.sh
RUN chmod +x dev/configure-sandbox.sh
RUN chmod +x dev/wait-for-it.sh
RUN chmod +x dev/ssh-copy-id.expect
RUN pip3 install coveralls

