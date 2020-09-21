FROM ubuntu:18.04

RUN apt-get -y update && apt-get install -y \
    openssh-server \
    singularity-container \
    git \
    python-pip \
    python3-pip \
    libfuse2 \
    vim

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

RUN mkdir /test

RUN mkdir -p /opt/plantit-cli-home \
    && mkdir -p /opt/plantit-cli
WORKDIR /opt/plantit-cli
COPY . ./
RUN chmod +x scripts/wait-for-it.sh \
    && pip3 install plantit-cli \
    && pip3 install -U pytest

SHELL ["/bin/bash", "-c"]
RUN echo $'if [ -d /etc/profile.d ]; then for i in /etc/profile.d/*.sh; do if [ -r $i ]; then . $i; fi done; fi' >> /etc/bash.bashrc
