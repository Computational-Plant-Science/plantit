# due to python 3.10 "loop argument must agree with lock" issue we use 3.11
#   - https://github.com/django/channels_redis/issues/278
#   - https://bugs.python.org/issue45416
FROM python:3.11-rc-bullseye
ENV PYTHONUNBUFFERED 1

RUN apt-get -y update && apt-get install -y \
    python3-numpy-dev \
    cron \
    postgresql-client \
    openssh-client \
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
    python3-vtk7

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

