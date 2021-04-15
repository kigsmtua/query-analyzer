#!/bin/bash

command=$1

case $command in

  cli)
    shift
    python3 app/app.py "$@"
    ;;

  test)
    python3 app/tests.py
    ;;
  migrate)
    PGPASSWORD=$DATABASE_PASSWORD psql -h db -U postgres < data/cpu_usage.sql
    PGPASSWORD=$DATABASE_PASSWORD psql -h db -U postgres -d homework -c "\COPY cpu_usage FROM data/cpu_usage.csv CSV HEADER"
    ;;
esac
