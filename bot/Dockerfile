FROM ubuntu:22.04
RUN apt update
RUN apt install -y python3 python3-pip
RUN pip install paramiko psycopg2-binary python-telegram-bot==13.7
RUN apt install -y openssh-server sysstat rsyslog net-tools
RUN echo "root:root" | chpasswd
RUN sed -i '/^#PermitRootLogin/c\PermitRootLogin yes' /etc/ssh/sshd_config
RUN  mkdir /app
WORKDIR /app
COPY . .
RUN chmod +x /app/docker_entrypoint.sh
CMD ["/app/docker_entrypoint.sh"]

