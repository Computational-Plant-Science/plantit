FROM python:3.13.3-bullseye
ENV PYTHONUNBUFFERED 1

# Use US mirror
RUN sed -i 's|http://deb.debian.org/debian|http://ftp.us.debian.org/debian|g' /etc/apt/sources.list

# Remove old lists, set retries, update and install packages with retries
RUN rm -rf /var/lib/apt/lists/* && \
    echo 'Acquire::Retries "5";' > /etc/apt/apt.conf.d/80-retries && \
    apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends \
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
    python3-vtk7

RUN mkdir /code
WORKDIR /code
COPY . ./
RUN pip install -r dockerfiles/plantit/requirements.txt
#RUN chmod +x scripts/configure-sandbox.sh
RUN chmod +x scripts/configure-superuser.sh
RUN chmod +x scripts/ssh-copy-id.expect
RUN chmod +x scripts/wait-for-it.sh
RUN chmod +x scripts/wait-for-postgres.sh
RUN pip3 install coveralls
