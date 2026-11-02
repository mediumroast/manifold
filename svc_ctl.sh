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
  admin <args> Run the host command inside the container: principals, credentials, roles, grants,
               settings, audit, export, purge (for example: $(basename "$0") production admin principal list).
               A file for a secret must be under /data, for example --secret-file /data/agent.secret.
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
  init-env|config|build|pull|start|start-fg|stop|down|restart|rebuild|status|logs|shell|health|admin|help|-h|--help)
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

env_value() {
  # The last KEY=value line of the environment file ("" if there is none).
  { grep -E "^$1=" "$ENV_FILE" 2>/dev/null || true; } | tail -1 | cut -d= -f2-
}

is_loopback() {
  case "$1" in
    127.*|::1|"[::1]"|localhost|LOCALHOST) return 0 ;;
    *) return 1 ;;
  esac
}

# The https:// addresses the certificate is made for: one per name in TLS_NAMES, on the served port.
caddy_sites() {
  local port names sites="" name
  port="$(env_value PORT)"; port="${port:-8686}"
  names="$(env_value TLS_NAMES)"; names="${names:-localhost 127.0.0.1}"
  for name in $names; do
    sites="${sites:+$sites, }https://$name:$port"
  done
  printf '%s' "$sites"
}

# The name whose certificate a client gets when it connects to an IP address (it sends no name then):
# the first non-loopback IP address in TLS_NAMES, else the first IP address, else the first name.
caddy_default_sni() {
  local names first_ip="" lan_ip="" name
  names="$(env_value TLS_NAMES)"; names="${names:-localhost 127.0.0.1}"
  for name in $names; do
    if [[ "$name" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ || "$name" == \[*\] ]]; then
      first_ip="${first_ip:-$name}"
      if ! is_loopback "$name"; then lan_ip="${lan_ip:-$name}"; fi
    fi
  done
  name="${lan_ip:-${first_ip:-${names%% *}}}"
  printf '%s' "${name#\[}" | tr -d ']'
}

compose() {
  export CADDY_SITES CADDY_DEFAULT_SNI
  CADDY_SITES="$(caddy_sites)"
  CADDY_DEFAULT_SNI="$(caddy_default_sni)"
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

# The instance repository must exist and hold manifold.yaml: otherwise the container would start
# and report itself unhealthy, which is a poor way to learn that WIKI_ROOT is still a placeholder.
ensure_instance() {
  local root
  root="$(sed -n 's/^WIKI_ROOT=//p' "$ENV_FILE" | tail -1)"
  [[ -n "$root" ]] || die "WIKI_ROOT is not set in $ENV_FILE. Set it to the absolute path of your instance repository."
  # Compose resolves a relative path against the folder that holds the compose file.
  [[ "$root" = /* ]] || root="$DOCKER_DIR/$root"
  [[ -d "$root" ]] || die "WIKI_ROOT in $ENV_FILE is not a folder: $root. Set it to the absolute path of your instance repository."
  [[ -f "$root/manifold.yaml" ]] || die "No manifold.yaml in $root (the WIKI_ROOT in $ENV_FILE). That folder is not an instance repository; see docs/quickstart.md."
}

# Make the data folder (security store and Caddy's files): private to you, outside the instance repository.
ensure_data_dir() {
  local data root
  data="$(env_value DATA_DIR)"
  [[ -n "$data" ]] || die "DATA_DIR is not set in $ENV_FILE. Set it to an absolute path outside your instance repository (init-env on a new file does this)."
  [[ "$data" = /* ]] || die "DATA_DIR in $ENV_FILE must be an absolute path (got '$data')."
  root="$(env_value WIKI_ROOT)"
  [[ "$root" = /* ]] || root="$DOCKER_DIR/$root"
  case "$data/" in
    "$root"/*) die "DATA_DIR ($data) is inside the instance repository ($root): the credential store would end up in git. Choose a folder outside it." ;;
  esac
  case "$root/" in
    "$data"/*) die "The instance repository ($root) is inside DATA_DIR ($data). Choose separate folders." ;;
  esac
  (umask 077; mkdir -p "$data" "$data/caddy/data" "$data/caddy/config")
  chmod 700 "$data" 2>/dev/null || true
}

# TLS is a setting: off (plain HTTP) or on (HTTPS). Plain HTTP on an address other than loopback
# is allowed only as a deliberate act, with a warning that cannot be missed.
check_tls() {
  local tls bind plain
  tls="$(env_value MANIFOLD_TLS)"; tls="${tls:-off}"
  [[ "$tls" == off || "$tls" == on ]] || die "MANIFOLD_TLS in $ENV_FILE must be 'off' or 'on' (got '$tls')."
  bind="$(env_value BIND_ADDRESS)"; bind="${bind:-127.0.0.1}"
  if [[ "$tls" == off ]] && ! is_loopback "$bind"; then
    plain="${MANIFOLD_ALLOW_PLAIN_ON_NETWORK:-$(env_value MANIFOLD_ALLOW_PLAIN_ON_NETWORK)}"
    if [[ "$plain" != yes ]]; then
      die "BIND_ADDRESS is $bind (reachable from the network) with MANIFOLD_TLS=off: credentials would cross the network in clear text. Set MANIFOLD_TLS=on in $ENV_FILE (see docs/tls.md), bind to 127.0.0.1, or, if the network is protected some other way, set MANIFOLD_ALLOW_PLAIN_ON_NETWORK=yes."
    fi
    warn "*** WARNING: serving plain HTTP on $bind. Credentials and wiki content cross the network unencrypted. ***"
  fi
}

warn_legacy_token() {
  if grep -q '^MANIFOLD_TOKEN=' "$ENV_FILE" 2>/dev/null; then
    warn "$ENV_FILE still has a MANIFOLD_TOKEN line. The shared token is no longer accepted; delete the line and use ./manifold admin to issue credentials."
  fi
}

# Everything 'start', 'restart' and friends need before compose runs.
prepare_start() {
  ensure_compose_file
  ensure_env_file
  ensure_instance
  ensure_data_dir
  check_tls
  warn_legacy_token
}

cmd_init_env() {
  ensure_compose_file
  if [[ -f "$ENV_FILE" ]]; then
    warn "Environment file already exists: $ENV_FILE"
    return 0
  fi

  [[ -f "$ENV_TEMPLATE" ]] || die "Template file not found: $ENV_TEMPLATE"
  # BIND_ADDRESS in the calling environment overrides the template; TLS follows it (off on loopback, on otherwise).
  local bind="${BIND_ADDRESS:-127.0.0.1}" tls="off" data="$SCRIPT_DIR/.manifold-data/$ENV_NAME" line
  is_loopback "$bind" || tls="on"
  : > "$ENV_FILE.tmp"
  chmod 600 "$ENV_FILE.tmp"
  while IFS= read -r line || [[ -n "$line" ]]; do
    case "$line" in
      DATA_DIR=) line="DATA_DIR=$data" ;;
      BIND_ADDRESS=*) line="BIND_ADDRESS=$bind" ;;
      MANIFOLD_TLS=*) line="MANIFOLD_TLS=$tls" ;;
    esac
    printf '%s\n' "$line" >> "$ENV_FILE.tmp"
  done < "$ENV_TEMPLATE"
  mv "$ENV_FILE.tmp" "$ENV_FILE"
  (umask 077; mkdir -p "$data/caddy/data" "$data/caddy/config")
  chmod 700 "$data"
  ok "Created $ENV_FILE from $(basename "$ENV_TEMPLATE") (DATA_DIR $data, MANIFOLD_TLS=$tls)"
  if [[ "$tls" == on ]]; then
    info "BIND_ADDRESS is $bind, so HTTPS is on. Add the names people use to TLS_NAMES and ALLOWED_HOSTS in $ENV_FILE; see docs/tls.md."
  fi
  info "No shared token is created. Credentials are issued to each person and agent: ./manifold init, or $0 $ENV_NAME admin credential issue ..."
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
  prepare_start
  info "Starting the wiki MCP service ($ENV_NAME)…"
  compose up -d --build
  ok "Service started."
}

cmd_start_fg() {
  prepare_start
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
  prepare_start
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
  prepare_start
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

cmd_admin() {
  ensure_compose_file
  ensure_env_file
  ensure_instance
  ensure_data_dir
  [[ ${#EXTRA_ARGS[@]} -gt 0 ]] || die "admin needs a command, for example: $0 $ENV_NAME admin principal list"
  # Use a terminal inside the container only when this one is a terminal (a secret is shown only on a terminal).
  local tty_flag=()
  if ! [[ -t 0 && -t 1 ]]; then
    tty_flag=(-T)
  fi
  local running
  running="$(compose ps --status running --quiet "$SERVICE_NAME" 2>/dev/null || true)"
  if [[ -n "$running" ]]; then
    compose exec ${tty_flag[@]+"${tty_flag[@]}"} "$SERVICE_NAME" python -m manifold_cli admin "${EXTRA_ARGS[@]}"
  else
    # No server yet (or it is stopped): run the command in a one-off container on the same data volume.
    if ! docker image inspect manifold-server:local >/dev/null 2>&1; then
      info "Building the image first ($ENV_NAME)…"
      compose build >&2
    fi
    compose run --rm --no-deps ${tty_flag[@]+"${tty_flag[@]}"} "$SERVICE_NAME" python -m manifold_cli admin "${EXTRA_ARGS[@]}"
  fi
}

cmd_health() {
  ensure_compose_file
  ensure_env_file
  ensure_instance
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
  admin) cmd_admin ;;
  help|-h|--help) usage ;;
  *) die "Unknown command '$COMMAND'. Use '$0 $ENV_NAME help' for usage." ;;
esac
