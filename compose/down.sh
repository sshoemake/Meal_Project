#!/bin/bash
# compose/down.sh

set -e

ENV=${1:-dev} # default to dev
ENV_FILE=".env.${ENV}"
shift 1                # remove first two args
ARGS="$@"              # remaining args

if [ ! -f "compose/${ENV_FILE}" ]; then
  echo "Environment file compose/${ENV_FILE} not found"
  exit 1
fi

export COMPOSE_ENV_FILE="compose/${ENV_FILE}"

# Compose files
COMPOSE_FILES="-f compose/docker-compose.yml -f compose/docker-compose.${ENV}.yml"

docker compose $COMPOSE_FILES --env-file "$COMPOSE_ENV_FILE" --profile $ENV down $ARGS
