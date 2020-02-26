#
# Container approximates a cluster for testing submitting jobs.
#

FROM ubuntu:18.04

RUN apt-get update && apt-get install -y openssh-server
RUN mkdir /var/run/sshd
RUN echo 'root:root' | chpasswd
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# SSH login fix. Otherwise user is kicked off after login
# RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]

RUN apt-get install -y curl vim

RUN apt-get install -y singularity-container

COPY ./dockerfiles/test_cluster/qsub /usr/bin

RUN apt-get update; apt-get install -y git python3 python3-pip
RUN mkdir -p /opt/; \
    cd /opt; \
    git clone https://github.com/cottersci/DIRT2_ClusterSide.git; \
    cd DIRT2_ClusterSide; \
    pip3 install -e .

RUN apt-get install libfuse2
RUN wget https://files.renci.org/pub/irods/releases/4.1.12/ubuntu14/irods-icommands-4.1.12-ubuntu14-x86_64.deb
RUN dpkg -i irods-icommands-4.1.12-ubuntu14-x86_64.deb
RUN rm irods-icommands-4.1.12-ubuntu14-x86_64.deb
COPY ./wait-for-it.sh /root/
COPY ./dockerfiles/test_cluster/irods_setup.sh /root/
