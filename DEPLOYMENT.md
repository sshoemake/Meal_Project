# Deployment & Operations (one-page)

This document summarizes production deployment details for the Meal Project and provides a minimal `.env` sample and commands to build/publish and run the production stack using the repository's `compose/docker-compose.prod.yml`.

## Project recap
- Django-based shopping & meal-planning application.
- Repo provides local dev instructions in `README.md` and a production compose file at `compose/docker-compose.prod.yml`.
- Production uses Traefik v3 as reverse proxy and `postgres:15` as the database.

## Files to check before deploy
- `compose/docker-compose.prod.yml` — production compose configuration (services: `traefik`, `web`, `db`).
- `traefik/traefik.yml`, `traefik/dynamic` and `traefik/acme.json` — Traefik configuration and Let's Encrypt storage (ensure `acme.json` exists and is writable by the Traefik container).
- `.env` — environment variables for Django and Postgres (not committed to repo).

## Minimal `.env` sample
Replace values before use.

DJANGO settings

DJANGO_ALLOWED_HOSTS=example.com
SECRET_KEY=replace_with_django_secret_key
DEBUG=0

Postgres settings

POSTGRES_USER=meal_user
POSTGRES_PASSWORD=supersecret
POSTGRES_DB=meal_db
POSTGRES_HOST=db
POSTGRES_PORT=5432

Other

# Host used by Traefik router label in compose
# Example: example.com
DJANGO_ALLOWED_HOSTS=example.com

Note: `compose/docker-compose.prod.yml` uses `env_file: .env`; ensure this file is present on the host running Docker Compose.

## Build and publish Docker image (example using GHCR)
Update `ghcr.io/YOUR_USER/YOUR_APP` in `compose/docker-compose.prod.yml` to your image path.

Build locally and test image:

```bash
# build
docker build -t meal_project:latest .
# run for quick smoke test (dev settings)
docker run --rm -it -p 8000:8000 -e DEBUG=1 meal_project:latest
```

Publish to GitHub Container Registry (example):

```bash
# login
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_GH_USER --password-stdin
# tag
docker tag meal_project:latest ghcr.io/YOUR_GH_USER/YOUR_REPO:latest
# push
docker push ghcr.io/YOUR_GH_USER/YOUR_REPO:latest
```

## Start production stack
Run from repo root (compose file path used below):

```bash
# (ensure .env is present and traefik/acme.json exists)
# start in detached mode
docker compose -f compose/docker-compose.prod.yml up -d
# view logs
docker compose -f compose/docker-compose.prod.yml logs -f
```

To stop and remove volumes:

```bash
docker compose -f compose/docker-compose.prod.yml down -v
```

## Traefik notes
- Traefik is configured to read Docker labels and uses `traefik/traefik.yml` + dynamic config in `traefik/dynamic`.
- `acme.json` stores TLS certs; give it `600` perms and ensure it is owner-writable by the user running Docker:

```bash
touch traefik/acme.json
chmod 600 traefik/acme.json
```

- `compose/docker-compose.prod.yml` routes the `web` service by host using `${DJANGO_ALLOWED_HOSTS}` — set that to your actual host.

## Database and persistence
- Postgres data is persisted to Docker volume `postgres_data` defined in the compose file.
- Healthcheck uses `pg_isready` with `${POSTGRES_USER}` and `${POSTGRES_DB}` to report readiness.

## Quick checklist before go-live
- [ ] Populate `.env` with production secrets
- [ ] Replace GHCR image path in `compose/docker-compose.prod.yml`
- [ ] Ensure `traefik/acme.json` exists and has `chmod 600`
- [ ] Confirm DNS for your host points to the machine running Traefik
- [ ] Start stack: `docker compose -f compose/docker-compose.prod.yml up -d`

---
Created to supplement `README.md` with a concise ops/deploy guide. Adjust values to your environment.

# Run in DEV:
docker compose -f compose/docker-compose.yml \
               -f compose/docker-compose.dev.yml \
               --env-file compose/.env.dev \
               --profile dev up
