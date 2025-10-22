#!/bin/sh
set -e

# If a config.py exists in the container it's used; otherwise generate from env vars
if [ ! -f /app/config.py ]; then
    if [ -z "$TOKEN" ]; then
        echo "ERROR: TOKEN environment variable is required" >&2
        exit 1
    fi
    cat > /app/config.py <<EOF
TOKEN = "$TOKEN"
CHAT_ID = ${CHAT_ID:-None}
EOF
fi

exec "$@"