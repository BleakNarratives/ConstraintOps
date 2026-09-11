#!/usr/bin/env bash
# serve.sh — persistent landing page server
# Run once: bash scripts/serve.sh
# Or add to crontab: */5 * * * * bash ~/ConstraintOps/scripts/serve.sh
# Checks if server is alive, starts it if not. Zero output if already running.

PORT=9123
SITE_DIR="$HOME/ConstraintOps/site"
PID_FILE="$HOME/ConstraintOps/state/server.pid"
LOG_FILE="$HOME/ConstraintOps/state/server.log"

# Check if existing server is alive
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        exit 0  # already running
    fi
fi

# Start fresh
mkdir -p "$(dirname "$PID_FILE")"
nohup "$HOME/venv/bin/python" -m http.server "$PORT" --bind 127.0.0.1 \
    --directory "$SITE_DIR" > "$LOG_FILE" 2>&1 < /dev/null &
echo $! > "$PID_FILE"
disown
