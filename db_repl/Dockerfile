FROM postgres:latest
ENV POSTGRES_PASSWORD=root
COPY setup.sh /setup.sh
RUN chmod +x /setup.sh
COPY entrypoint-replica.sh /entrypoint-replica.sh
RUN chmod +x /entrypoint-replica.sh
ENTRYPOINT ["/entrypoint-replica.sh"]
