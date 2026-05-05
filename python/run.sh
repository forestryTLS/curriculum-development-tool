#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$ROOT/.venv"
SERVICES=(
  "lo_mapping_service"
  "syllabi_service"
)

create_venv_if_needed() {
  if [ ! -d "$VENV" ]; then
    echo "Creating shared virtual environment in $VENV"
    python3 -m venv "$VENV"
  fi
}

activate_venv() {
  # shellcheck source=/dev/null
  source "$VENV/bin/activate"
}

install_dependencies() {
  local requirements_file="$1"

  if [ -f "$requirements_file" ]; then
    echo "Installing dependencies from $requirements_file"
    pip install -r "$requirements_file"
  fi
}

read_service_config() {
  local main_file="$1"
  local app_target
  local port

  app_target=$(sed -n 's/.*Config("\([^"]*\)".*/\1/p' "$main_file" | head -n 1)
  port=$(sed -n 's/.*port=\([0-9][0-9]*\).*/\1/p' "$main_file" | head -n 1)

  if [ -z "$app_target" ] || [ -z "$port" ]; then
    return 1
  fi

  printf '%s|%s\n' "$app_target" "$port"
}

start_service() {
  local service_name="$1"
  local service_root="$ROOT/services/$service_name"
  local main_file="$service_root/app/main.py"
  local service_config
  local app_target
  local port

  if [ ! -d "$service_root" ]; then
    echo "Skipping $service_name because $service_root was not found"
    return 0
  fi

  if [ ! -f "$main_file" ]; then
    echo "Skipping $service_name because $main_file was not found"
    return 0
  fi

  service_config=$(read_service_config "$main_file") || {
    echo "Skipping $service_name because app target or port could not be read from $main_file"
    return 0
  }

  IFS="|" read -r app_target port <<< "$service_config"

  echo "Starting $service_name on http://127.0.0.1:$port"
  (
    cd "$service_root"
    uvicorn "$app_target" --reload --host 127.0.0.1 --port "$port"
  ) &
}

cleanup() {
  echo
  echo "Stopping FastAPI services..."
  jobs -p | xargs -r kill
}

trap cleanup EXIT SIGINT SIGTERM

create_venv_if_needed
activate_venv

for service in "${SERVICES[@]}"; do
  install_dependencies "$ROOT/services/$service/requirements.txt"
done

echo
echo "Launching FastAPI services..."
for service in "${SERVICES[@]}"; do
  start_service "$service"
done

echo
echo "Press Ctrl+C to stop them."

wait
