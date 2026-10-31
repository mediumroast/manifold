#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_DIR="$SCRIPT_DIR/docker"
COMPOSE_FILE="$DOCKER_DIR/docker-compose.yml"
COMPOSE_DEV_FILE="$DOCKER_DIR/docker-compose.dev.yml"
PROJECT_NAME_BASE="manifold"
SERVICE_NAME="manifold"

_TTY=false
if [[ -t 1 ]]; then
  _TTY=true
fi

_red() { if "$_TTY"; then printf '\033[0;31m%s\033[0m' "$*"; else printf '%s' "$*"; fi; }
_green() { if "$_TTY"; then printf '\033[0;32m%s\033[0m' "$*"; else printf '%s' "$*"; fi; }
_yellow() { if "$_TTY"; then printf '\033[0;33m%s\033[0m' "$*"; else printf '%s' "$*"; fi; }
_bold() { if "$_TTY"; then printf '\033[1m%s\033[0m' "$*"; else printf '%s' "$*"; fi; }

info() { printf '  %s %s\n' "$( _bold "[wiki]" )" "$*"; }
ok() { printf '  %s %s\n' "$( _green "✓" )" "$*"; }
warn() { printf '  %s %s\n' "$( _yellow "!" )" "$*" >&2; }
die() { printf '  %s %s\n' "$( _red "✗" )" "$*" >&2; exit 1; }

COMPOSE_CMD=()
if docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD=(docker-compose)
else
  die "Neither 'docker compose' nor 'docker-compose' is available."
fi

# Pass the calling shell's UID/GID into compose so the container does not
# run as root.  Files written by the server (handoffs, sidebar, log) will be
# owned by the host user, keeping git operations on the host side clean.
export HOST_UID=$(id -u)
export HOST_GID=$(id -g)

usage() {
  cat <<EOF
Usage: $(basename "$0") <environment> <command> [options]
   or: $(basename "$0") <command> <environment> [options]

Environments: dev | staging | production
Commands:
  init-env     Create the environment file from its template
  config       Show resolved compose configuration
  build        Build the container image
  pull         Pull the base image used by the Dockerfile
  start        Start the service in detached mode
  start-fg     Start the service in the foreground
  stop         Stop and remove the service
  restart      Recreate the service
  rebuild      Pull base image, rebuild, and recreate the service
  status       Show service status
  logs [svc]   Tail logs for the service
  shell [svc]  Open a shell in the service container
  health       Validate the mounted wiki and container wiring
EOF
  exit 1
}

if [[ $# -eq 1 ]] && [[ "$1" =~ ^(help|-h|--help)$ ]]; then
  usage
fi

if [[ $# -lt 2 ]]; then
  usage
fi

ENV_NAME=""
COMMAND=""

case "$1" in
  dev|staging|production)
    ENV_NAME="$1"
    COMMAND="$2"
    ;;
  init-env|config|build|pull|start|start-fg|stop|down|restart|rebuild|status|logs|shell|health|help|-h|--help)
    if [[ "$2" =~ ^(help|-h|--help)$ ]]; then
      usage
    fi
    COMMAND="$1"
    ENV_NAME="$2"
    ;;
  *)
    ENV_NAME="$1"
    COMMAND="$2"
    ;;
esac

shift 2
EXTRA_ARGS=("$@")

case "$ENV_NAME" in
  dev|staging|production) ;;
  *) die "Unknown environment '$ENV_NAME'. Use dev, staging, or production." ;;
esac

ENV_FILE="$DOCKER_DIR/.env.$ENV_NAME"
ENV_TEMPLATE="$ENV_FILE.template"

compose() {
  local files=(--file "$COMPOSE_FILE")
  # Only the dev environment mounts the source and reloads.
  if [[ "$ENV_NAME" == "dev" ]]; then
    files+=(--file "$COMPOSE_DEV_FILE")
  fi
  "${COMPOSE_CMD[@]}" \
    --project-name "$PROJECT_NAME_BASE-$ENV_NAME" \
    --env-file "$ENV_FILE" \
    "${files[@]}" \
    "$@"
}

ensure_compose_file() {
  [[ -f "$COMPOSE_FILE" ]] || die "Compose file not found: $COMPOSE_FILE"
}

ensure_env_file() {
  [[ -f "$ENV_FILE" ]] || die "Environment file not found: $ENV_FILE. Run '$0 $ENV_NAME init-env'."
}

cmd_init_env() {
  ensure_compose_file
  if [[ -f "$ENV_FILE" ]]; then
    warn "Environment file already exists: $ENV_FILE"
    return 0
  fi

  [[ -f "$ENV_TEMPLATE" ]] || die "Template file not found: $ENV_TEMPLATE"
  cp "$ENV_TEMPLATE" "$ENV_FILE"
  # Generate the shared token so the service can start; keep the file private.
  local token
  token="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
  sed "s|^MANIFOLD_TOKEN=.*|MANIFOLD_TOKEN=$token|" "$ENV_FILE" > "$ENV_FILE.tmp" && mv "$ENV_FILE.tmp" "$ENV_FILE"
  chmod 600 "$ENV_FILE"
  ok "Created $ENV_FILE from $(basename "$ENV_TEMPLATE") with a new MANIFOLD_TOKEN"
  info "Clients send it as 'Authorization: Bearer <token>'; a browser asks for it as the password (any user name)."
}

cmd_config() {
  ensure_compose_file
  ensure_env_file
  info "Resolved compose configuration for $ENV_NAME"
  compose config
}

cmd_build() {
  ensure_compose_file
  ensure_env_file
  info "Building the wiki MCP image ($ENV_NAME)…"
  compose build
  ok "Build complete."
}

cmd_pull() {
  info "Pulling the base Python image for $ENV_NAME…"
  docker pull python:3.12-slim
  ok "Base image updated."
}

cmd_start() {
  ensure_compose_file
  ensure_env_file
  info "Starting the wiki MCP service ($ENV_NAME)…"
  compose up -d --build
  ok "Service started."
}

cmd_start_fg() {
  ensure_compose_file
  ensure_env_file
  info "Starting the wiki MCP service in the foreground ($ENV_NAME)…"
  compose up --build
}

cmd_stop() {
  ensure_compose_file
  ensure_env_file
  info "Stopping the wiki MCP service ($ENV_NAME)…"
  compose down
  ok "Service stopped."
}

cmd_restart() {
  ensure_compose_file
  ensure_env_file
  info "Stopping the wiki MCP service ($ENV_NAME)…"
  compose down
  ok "Service stopped."
  info "Building the wiki MCP image ($ENV_NAME)…"
  compose build
  ok "Build complete."
  info "Starting the wiki MCP service ($ENV_NAME)…"
  compose up -d
  ok "Service restarted."
}

cmd_rebuild() {
  ensure_compose_file
  ensure_env_file
  info "Pulling base image and rebuilding the wiki MCP service ($ENV_NAME)…"
  compose build --pull --no-cache
  compose up -d --force-recreate
  ok "Rebuild complete."
}

cmd_status() {
  ensure_compose_file
  ensure_env_file
  compose ps
}

cmd_logs() {
  ensure_compose_file
  ensure_env_file
  local svc="${EXTRA_ARGS[0]:-$SERVICE_NAME}"
  info "Streaming logs for $svc ($ENV_NAME)…"
  compose logs -f "$svc"
}

cmd_shell() {
  ensure_compose_file
  ensure_env_file
  local svc="${EXTRA_ARGS[0]:-$SERVICE_NAME}"
  info "Opening a shell in $svc ($ENV_NAME)…"
  compose run --rm --entrypoint /bin/sh "$svc"
}

cmd_health() {
  ensure_compose_file
  ensure_env_file
  info "Checking wiki mount and container wiring ($ENV_NAME)…"
  compose run --rm --no-deps --entrypoint python "$SERVICE_NAME" -c '
import os, sys
from pathlib import Path
from wiki_backend.health import wiki_health
ok, payload = wiki_health(Path(os.environ["CONTAINER_WIKI_ROOT"]))
print(payload["message"])
for name, state in payload["checks"].items():
    print("  %-20s %s" % (name, state))
sys.exit(0 if ok else 1)
'
  ok "Health check passed."
}

case "$COMMAND" in
  init-env) cmd_init_env ;;
  config) cmd_config ;;
  build) cmd_build ;;
  pull) cmd_pull ;;
  start) cmd_start ;;
  start-fg) cmd_start_fg ;;
  stop|down) cmd_stop ;;
  restart) cmd_restart ;;
  rebuild) cmd_rebuild ;;
  status) cmd_status ;;
  logs) cmd_logs ;;
  shell) cmd_shell ;;
  health) cmd_health ;;
  help|-h|--help) usage ;;
  *) die "Unknown command '$COMMAND'. Use '$0 $ENV_NAME help' for usage." ;;
esac
