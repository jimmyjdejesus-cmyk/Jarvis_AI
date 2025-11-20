#!/usr/bin/env bash
set -euo pipefail

# Dev start script: ensures backend launchd service is installed and running,
# waits for backend health endpoint then starts the frontend dev server.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NAME=com.jimmy.jarvis
FRONTEND_DIR="$HOME/Documents/agent-ui/frontend"
BACKEND_PORT=${1:-8000}
FRONTEND_PORT=${2:-5173}
HEALTH_TIMEOUT=${3:-30}

echo "Starting dev flow: backend port=$BACKEND_PORT frontend port=$FRONTEND_PORT"

# Ensure the service is installed and configured for the requested port
echo "Installing/ensuring backend service form launchd..."
"$ROOT/scripts/service-manager.sh" install "$BACKEND_PORT"

echo "Waiting for backend health (timeout=${HEALTH_TIMEOUT}s)..."
end=$((SECONDS+HEALTH_TIMEOUT))
while [ $SECONDS -lt $end ]; do
  if curl -s "http://127.0.0.1:${BACKEND_PORT}/api/v1/health" >/dev/null 2>&1; then
    echo "Backend healthy."
    break
  fi
  echo -n '.'; sleep 1
done
if [ $SECONDS -ge $end ]; then
  echo "Backend health check failed after ${HEALTH_TIMEOUT}s" >&2
  exit 1
fi

# Start frontend dev server
if [ ! -d "$FRONTEND_DIR" ]; then
  echo "Frontend directory not found: $FRONTEND_DIR" >&2
  exit 1
fi

cd "$FRONTEND_DIR"

# Choose package manager and start dev server
if command -v pnpm >/dev/null 2>&1; then
  PM=pnpm
elif command -v yarn >/dev/null 2>&1; then
  PM=yarn
else
  PM=npm
fi

echo "Using package manager: $PM"
echo "VITE_API_BASE=http://127.0.0.1:${BACKEND_PORT}/api"

export VITE_API_BASE="http://127.0.0.1:${BACKEND_PORT}/api"

if [ "$PM" = "pnpm" ]; then
  pnpm install
  pnpm dev -- --port $FRONTEND_PORT
elif [ "$PM" = "yarn" ]; then
  yarn install
  yarn dev --port $FRONTEND_PORT
else
  npm install
  npm run dev -- --host 0.0.0.0 --port $FRONTEND_PORT
fi
