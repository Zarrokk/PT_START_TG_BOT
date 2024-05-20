#!/bin/bash
echo 'replication_image_started'
while ! (echo > /dev/tcp/db_image/5432) >/dev/null 2>&1; do
  sleep 1
  echo 'checking alive'
done

su -p postgres -c /setup.sh
