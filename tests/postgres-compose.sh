#!/usr/bin/env bash
set -euo pipefail

# Use a separate project, volume and container even if the student's stack is running.
project="agno-test-${RANDOM}-$$"
override=$1
printf 'services:\n  agentos-db:\n    container_name: %s-db\n' "$project" > "$override"
compose=(docker compose --env-file /dev/null -p "$project" -f compose.yaml -f "$override")
DB_PASS="$(openssl rand -hex 32)"
export DB_PASS OPENAI_API_KEY=fixture
trap '"${compose[@]}" down -v' EXIT

if DB_PASS=ai "${compose[@]}" run --rm --no-deps agentos-db true; then
    echo 'PostgreSQL started with the former default password' >&2
    exit 1
fi
"${compose[@]}" up -d agentos-db
for _ in {1..60}; do
    if "${compose[@]}" exec -T agentos-db pg_isready -h agentos-db -U ai -d ai; then break; fi
    sleep 2
done
"${compose[@]}" exec -T agentos-db sh -ec 'PGPASSWORD="$POSTGRES_PASSWORD" psql -w -h agentos-db -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1"'
if "${compose[@]}" exec -T -e PGPASSWORD=ai agentos-db psql -w -h agentos-db -U ai -d ai -c 'SELECT 1'; then
    echo 'PostgreSQL authenticated the former default password' >&2
    exit 1
fi
