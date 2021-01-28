FROM python:buster
ENV PYTHONUNBUFFERED 1

RUN apt-get -y update && apt-get install -y \
    python3-numpy-dev \
    cron \
    postgresql-client \
    openssh-client \
    sshpass \
    curl \
    vim \
    expect

RUN mkdir /code
WORKDIR /code
COPY . ./
RUN pip install -r dockerfiles/plantit/requirements.txt
RUN chmod +x scripts/configure-sandbox.sh
RUN chmod +x scripts/configure-superuser.sh
RUN chmod +x scripts/ssh-copy-id.expect
RUN chmod +x scripts/wait-for-it.sh
RUN chmod +x scripts/wait-for-postgres.sh
RUN pip3 install coveralls

