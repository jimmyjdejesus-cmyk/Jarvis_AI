#!/usr/bin/env bash
set -euo pipefail

NAME=com.jimmy.jarvis
PLIST_PATH="$(pwd)/scripts/launchd/${NAME}.plist"
DEST=~/Library/LaunchAgents/${NAME}.plist

if [[ "$EUID" -eq 0 ]]; then
  echo "Warning: Running as root is not recommended for user LaunchAgents. Use your normal user account."
fi

case "${1:-}" in
  install)
    PORT=${2:-${PORT:-8000}}
    mkdir -p "$(dirname "$DEST")"
    # Replace port placeholder in the plist so the installed service binds to the correct port
    sed "s/__PORT__/${PORT}/g" "$PLIST_PATH" > "$DEST"
    # Unload first to be safe
    launchctl unload "$DEST" 2>/dev/null || true
    launchctl load -w "$DEST"
    echo "Installed and loaded launchd service ${NAME} (port=${PORT})."
    ;;
  start)
    launchctl start "$NAME"
    echo "Start signal sent to ${NAME}."
    ;;
  stop)
    launchctl stop "$NAME"
    echo "Stop signal sent to ${NAME}."
    ;;
  restart)
    launchctl stop "$NAME" 2>/dev/null || true
    sleep 1
    launchctl start "$NAME"
    echo "Restarted ${NAME}."
    ;;
  uninstall)
    launchctl unload "$DEST" 2>/dev/null || true
    rm -f "$DEST"
    echo "Uninstalled ${NAME}."
    ;;
  status)
    if launchctl list | grep -q "$NAME"; then
      launchctl list | grep "$NAME"
    else
      echo "Service ${NAME} not loaded or not running."
    fi
    ;;
  *)
    echo "Usage: $0 {install|start|stop|restart|uninstall|status}"
    exit 1
    ;;
esac
