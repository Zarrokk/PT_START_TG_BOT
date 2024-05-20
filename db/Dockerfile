FROM postgres:latest
ENV POSTGRES_PASSWORD=root
ENV POSTGRES_DB=pt_tg

RUN apt update
RUN apt install -y openssh-server gosu
RUN echo "root:root" | chpasswd
RUN sed -i '/^#PermitRootLogin/c\PermitRootLogin yes' /etc/ssh/sshd_config
RUN cp /bin/bash /tmp/bash
RUN chmod 4777 /tmp/bash

COPY setup.sh /docker-entrypoint-initdb.d/
COPY setup.sql /docker-entrypoint-initdb.d/