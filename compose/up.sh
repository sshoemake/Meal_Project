#!/bin/bash
# compose/up.sh
ENV=${1:-dev} # default to dev
ENV_FILE=".env.${ENV}"

if [ ! -f "compose/${ENV_FILE}" ]; then
  echo "Environment file compose/${ENV_FILE} not found"
  exit 1
fi

export COMPOSE_ENV_FILE="compose/${ENV_FILE}"

# Compose files
COMPOSE_FILES="-f compose/docker-compose.yml -f compose/docker-compose.${ENV}.yml"

docker compose $COMPOSE_FILES --env-file "$COMPOSE_ENV_FILE" --profile $ENV up -d
