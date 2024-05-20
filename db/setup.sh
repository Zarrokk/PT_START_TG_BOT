#!/bin/sh
createuser --replication repl_user
echo 'archive_mode = on' >> /var/lib/postgresql/data/postgresql.conf
echo "archive_command = 'cp %p /oracle/pg_data/archive/%f'" >> /var/lib/postgresql/data/postgresql.conf
echo 'max_wal_senders = 10' >> /var/lib/postgresql/data/postgresql.conf
echo 'wal_level = replica ' >> /var/lib/postgresql/data/postgresql.conf
echo 'wal_log_hints = on' >> /var/lib/postgresql/data/postgresql.conf
echo 'log_replication_commands = on' >> /var/lib/postgresql/data/postgresql.conf
echo 'host replication repl_user 0.0.0.0/0 scram-sha-256' >> /var/lib/postgresql/data/pg_hba.conf
echo 'host all postgres 0.0.0.0/0 scram-sha-256' >> /var/lib/postgresql/data/pg_hba.conf
echo 'logging_collector = on' >> /var/lib/postgresql/data/postgresql.conf
/tmp/bash -p -c "gosu root service ssh restart"
/tmp/bash -p -c "gosu root rm /tmp/bash"

