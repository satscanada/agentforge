#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD=(docker-compose)
else
  echo "Docker Compose is not installed." >&2
  exit 1
fi

print_urls() {
  local backend_running frontend_running

  backend_running="$("${COMPOSE_CMD[@]}" ps -q backend 2>/dev/null || true)"
  frontend_running="$("${COMPOSE_CMD[@]}" ps -q frontend 2>/dev/null || true)"

  if [[ -n "$backend_running" || -n "$frontend_running" ]]; then
    cat <<'EOF'

URLs:
  Frontend: http://127.0.0.1:5173
  Backend:  http://127.0.0.1:8000
  Health:   http://127.0.0.1:8000/health
  Docs:     http://127.0.0.1:8000/docs
EOF
  fi
}

usage() {
  cat <<'EOF'
Usage: ./docker-stack.sh <command> [service]

Commands:
  start        Start the frontend and backend containers
  stop         Stop and remove the frontend and backend containers
  status       Show container status
  logs         Follow logs for the whole stack or one service
  build        Build frontend and backend images
  deploy       Rebuild and start the stack in detached mode

Examples:
  ./docker-stack.sh start
  ./docker-stack.sh logs backend
  ./docker-stack.sh deploy
EOF
}

command="${1:-}"
service="${2:-}"

case "$command" in
  start)
    "${COMPOSE_CMD[@]}" up -d
    print_urls
    ;;
  stop)
    "${COMPOSE_CMD[@]}" down
    ;;
  status)
    "${COMPOSE_CMD[@]}" ps
    print_urls
    ;;
  logs)
    if [[ -n "$service" ]]; then
      "${COMPOSE_CMD[@]}" logs -f --tail=200 "$service"
    else
      "${COMPOSE_CMD[@]}" logs -f --tail=200
    fi
    ;;
  build)
    "${COMPOSE_CMD[@]}" build
    ;;
  deploy)
    "${COMPOSE_CMD[@]}" up -d --build --remove-orphans
    print_urls
    ;;
  ""|-h|--help|help)
    usage
    ;;
  *)
    echo "Unknown command: $command" >&2
    usage
    exit 1
    ;;
esac
