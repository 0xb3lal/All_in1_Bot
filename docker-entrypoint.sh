#!/bin/bash#!/bin/sh

set -eset -e



# Generate config.py if it doesn't exist# If a config.py exists in the container it's used; otherwise generate from env vars

if [ ! -f /app/config.py ]; thenif [ ! -f /app/config.py ]; then

    if [ -z "$TOKEN" ]; then    if [ -z "$TOKEN" ]; then

        echo "ERROR: TOKEN environment variable is required if config.py is not provided"        echo "ERROR: TOKEN environment variable is required" >&2

        exit 1        exit 1

    fi    fi

        cat > /app/config.py <<EOF

    echo "Generating config.py from environment variables..."TOKEN = "$TOKEN"

    echo "TOKEN = \"$TOKEN\"" > /app/config.pyCHAT_ID = ${CHAT_ID:-None}

    EOF

    if [ ! -z "$CHAT_ID" ]; thenfi

        echo "CHAT_ID = \"$CHAT_ID\"" >> /app/config.py

    fiexec "$@"
fi

exec "$@"