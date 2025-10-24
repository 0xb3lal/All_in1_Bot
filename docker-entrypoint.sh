#!/usr/bin/env bash
set -euo pipefail

if [ ! -f /app/config.py ]; then
    [ -z "${TOKEN:-}" ] && { echo "ERROR: TOKEN env var required" >&2; exit 1; }

    cat > /app/config.py <<-EOF
TOKEN = "${TOKEN}"
EOF

    [ -n "${CHAT_ID:-}" ] && echo "CHAT_ID = \"${CHAT_ID}\"" >> /app/config.py
fi

exec "$@"
