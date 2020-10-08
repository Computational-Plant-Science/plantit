FROM ubuntu:18.04
SHELL ["/bin/bash", "-c"]

RUN apt-get -y update && apt-get install -y \
    openssh-server \
    build-essential \
    libssl-dev \
    uuid-dev \
    libgpgme11-dev \
    squashfs-tools \
    libseccomp-dev \
    wget \
    pkg-config \
    git \
    python-pip \
    python3-pip \
    libfuse2 \
    vim \
    tzdata

RUN mkdir /var/run/sshd
RUN echo 'root:root' | chpasswd
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/#PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config

# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]

RUN export VERSION=1.15.2 OS=linux ARCH=amd64 && \
    wget https://dl.google.com/go/go$VERSION.$OS-$ARCH.tar.gz && \
    tar -C /usr/local -xzvf go$VERSION.$OS-$ARCH.tar.gz && \
    rm go$VERSION.$OS-$ARCH.tar.gz && \
    export VERSION=3.6.3 && \
    wget https://github.com/sylabs/singularity/releases/download/v${VERSION}/singularity-${VERSION}.tar.gz && \
    tar -xzf singularity-${VERSION}.tar.gz

ENV PATH="/usr/local/go/bin:${PATH}"

RUN cd singularity && \
    ./mconfig && \
    make -C builddir && \
    make -C builddir install

RUN mkdir /test && \
    mkdir -p /opt/plantit-cli-home && \
    mkdir -p /opt/plantit-cli

WORKDIR /opt/plantit-cli
COPY . ./
RUN chmod +x scripts/wait-for-it.sh \
    && pip3 install plantit-cli \
    && pip3 install -U pytest

RUN echo $'if [ -d /etc/profile.d ]; then for i in /etc/profile.d/*.sh; do if [ -r $i ]; then . $i; fi done; fi' >> /etc/bash.bashrc
