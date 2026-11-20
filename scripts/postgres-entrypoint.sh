#!/bin/sh
set +x

case "$POSTGRES_PASSWORD" in
    ai) ;;
    *[![:space:]]*) exec docker-entrypoint.sh "$@" ;;
esac
echo 'Set a unique PostgreSQL password in DB_PASS.' >&2
exit 1
