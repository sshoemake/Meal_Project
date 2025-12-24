#!/bin/bash
# scripts/manage.sh
# Usage: ./manage.sh <env> <command> [args]

set -e

ENV=${1:-dev}          # dev / uat / prod
COMMAND=${2:-migrate}  # default command
shift 2                # remove first two args
ARGS="$@"              # remaining args

ENV_FILE="compose/.env.${ENV}"

if [ ! -f "$ENV_FILE" ]; then
  echo "Environment file $ENV_FILE not found"
  exit 1
fi

# Load environment variables
export $(grep -v '^#' "$ENV_FILE" | xargs)

# Compose files for non-dev environments
COMPOSE_FILES="-f compose/docker-compose.yml"
if [[ "$ENV" != "dev" && -f "compose/docker-compose.${ENV}.yml" ]]; then
  COMPOSE_FILES="$COMPOSE_FILES -f compose/docker-compose.${ENV}.yml"
fi

if [ "$ENV" == "dev" ]; then
  echo "[DEV] Running Django command locally: $COMMAND $ARGS"
  python manage.py $COMMAND $ARGS
else
  echo "[$ENV] Running Django command inside Docker: $COMMAND $ARGS"
  docker compose $COMPOSE_FILES --env-file "$ENV_FILE" --profile $ENV run --rm web python manage.py $COMMAND $ARGS
fi
