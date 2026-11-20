#!/bin/bash
set +x

############################################################################
#
#    Agno Container Entrypoint
#
############################################################################

# Colors
ORANGE='\033[38;5;208m'
DIM='\033[2m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${ORANGE}"
cat << 'BANNER'
     █████╗  ██████╗ ███╗   ██╗ ██████╗
    ██╔══██╗██╔════╝ ████╗  ██║██╔═══██╗
    ███████║██║  ███╗██╔██╗ ██║██║   ██║
    ██╔══██║██║   ██║██║╚██╗██║██║   ██║
    ██║  ██║╚██████╔╝██║ ╚████║╚██████╔╝
    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝
BANNER
echo -e "${NC}"

if [[ "$WAIT_FOR_DB" = true || "$WAIT_FOR_DB" = True ]]; then
    if [[ -n "$DB_HOST" ]]; then
        DB_WAIT_TARGET="${DB_HOST}:${DB_PORT:-5432}"
    elif [[ -n "$DATABASE_URL" ]]; then
        DB_WAIT_TARGET="$(python - 2>/dev/null <<'PY'
from os import getenv
from urllib.parse import urlparse

parsed = urlparse(getenv("DATABASE_URL", ""))
if parsed.hostname:
    print(f"{parsed.hostname}:{parsed.port or 5432}")
PY
)" || { echo "Invalid database configuration." >&2; exit 1; }
    else
        DB_WAIT_TARGET=""
    fi

    if [[ -n "$DB_WAIT_TARGET" ]]; then
        echo -e "    ${DIM}Waiting for database...${NC}"
        if ! dockerize -wait "tcp://$DB_WAIT_TARGET" -timeout 300s >/dev/null 2>&1; then
            echo "Database unavailable. Check the connection settings." >&2
            exit 1
        fi
        echo -e "    ${BOLD}Database ready.${NC}"
        echo ""
    else
        echo -e "    ${DIM}WAIT_FOR_DB=True, but no DB_HOST or DATABASE_URL was provided. Skipping database wait.${NC}"
    fi
fi

PORT_VALUE="${PORT:-8000}"

case "$1" in
    chill)
        echo -e "    ${DIM}Mode: chill${NC}"
        echo -e "    ${BOLD}Container running.${NC}"
        echo ""
        while true; do sleep 18000; done
        ;;
    serve)
        echo -e "    ${DIM}Mode: serve${NC}"
        echo -e "    ${BOLD}Starting AgentOS on 0.0.0.0:${PORT_VALUE}.${NC}"
        echo ""
        exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT_VALUE" --no-access-log
        ;;
    *)
        exec "$@"
        ;;
esac
