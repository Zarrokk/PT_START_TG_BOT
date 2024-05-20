#!/bin/bash
service ssh start
rsyslogd
while ! (echo > /dev/tcp/db_image/5432) >/dev/null 2>&1; do
  sleep 1
  echo 'checking alive'
done
python3 main.py