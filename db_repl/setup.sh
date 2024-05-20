#!bin/sh

rm -rf $PGDATA/*
export PGPASSWORD=123
pg_basebackup -h db_image -D $PGDATA -U repl_user -X stream -R
chmod 0700 /var/lib/postgresql/data

/usr/lib/postgresql/16/bin/postgres
