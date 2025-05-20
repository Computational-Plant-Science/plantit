#FROM python:3.13.3-bullseye
FROM python:3.11-slim
ENV PYTHONUNBUFFERED 1

RUN apt-get -y update && apt-get install -y \
    python3-numpy-dev \
    cron \
    postgresql-client \
    default-mysql-client \
    openssh-client \
    iputils-ping \
    sshpass \
    curl \
    vim \
    expect \
    zlib1g-dev \
    libjpeg-dev \
    python3-pythonmagick \
    inkscape \
    xvfb \
    poppler-utils \
    libfile-mimeinfo-perl \
    qpdf \
    libimage-exiftool-perl \
    # ufraw-batch \
    ffmpeg \
    scribus \
    libreoffice \
    python3-vtk9

RUN mkdir /code
WORKDIR /code
COPY . ./
# Ensure pip < 24.1 to avoid metadata issues
RUN pip install "pip<24.1"

RUN pip install -r dockerfiles/plantit/requirements.txt
#RUN chmod +x scripts/configure-sandbox.sh
RUN chmod +x scripts/configure-superuser.sh
RUN chmod +x scripts/ssh-copy-id.expect
RUN chmod +x scripts/wait-for-it.sh
RUN chmod +x scripts/wait-for-postgres.sh
RUN pip3 install coveralls
