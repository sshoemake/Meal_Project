
# Deployment & Operations

This document summarizes development, UAT, and production deployment procedures for the Meal Project.

Production uses Docker Compose, a PostgreSQL database, and a separately managed Traefik reverse proxy.

## Project Overview

- Django-based shopping and meal-planning application.
- PostgreSQL 18 database.
- Docker images published to GitHub Container Registry (GHCR).
- Production reverse proxy and TLS managed independently by Traefik.

## Important Files

| File | Purpose |
|---|---|
| `compose/docker-compose.yml` | Base Compose configuration |
| `compose/docker-compose.dev.yml` | Development configuration |
| `compose/docker-compose.uat.yml` | UAT configuration |
| `compose/docker-compose.prod.yml` | Production configuration |
| `compose/.env.dev` | Development environment variables |
| `compose/.env.uat` | UAT environment variables |
| `compose/.env.prod` | Production environment variables |
| `compose/up.sh` | Environment startup helper |
| `compose/down.sh` | Environment shutdown helper |
| `compose/manage.sh` | Django management command helper |

Environment files contain secrets and must not be committed to Git.

## Environment Configuration

Production uses `compose/.env.prod`.

Example variables:

```dotenv
# Django
DJANGO_ALLOWED_HOSTS=example.com
SECRET_KEY=replace_with_django_secret_key
DEBUG=0

# PostgreSQL
POSTGRES_USER=meal_user
POSTGRES_PASSWORD=replace_with_secure_password
POSTGRES_DB=meal_db
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

Replace example values with actual production settings.

The production Compose configuration uses `env_file: .env.prod` for the application and database containers.

The production hostname must also match the host rule defined in the Traefik labels in `compose/docker-compose.prod.yml`. Updating `DJANGO_ALLOWED_HOSTS` alone does not change Traefik's routing rule.

## Docker Image Build and Publishing

Production images are published to GitHub Container Registry.

Example local build:

```bash
docker build -t meal_project:latest .
```

Quick local smoke test:

```bash
docker run --rm -it -p 8000:8000 \
  -e DEBUG=1 \
  meal_project:latest
```

Publish an image to GHCR:

```bash
# Authenticate
echo "$GITHUB_TOKEN" | docker login ghcr.io \
  -u YOUR_GH_USER --password-stdin

# Tag
docker tag meal_project:latest \
  ghcr.io/YOUR_GH_USER/YOUR_REPO:latest

# Push
docker push ghcr.io/YOUR_GH_USER/YOUR_REPO:latest
```

Update the image reference in the production Compose configuration when deploying a new version.

## Reverse Proxy and TLS

Traefik is managed separately in the
[homelab_infrastructure](https://github.com/sshoemake/homelab_infrastructure)
repository.

Meal Project does not manage Traefik, its configuration, TLS certificates, or ACME storage.

Before deploying the production application, verify:

- The standalone Traefik service is running.
- The external Docker network `traefik_public` exists.
- The web container is attached to `traefik_public`.
- The Traefik file provider has loaded the `security-headers` middleware.
- DNS for the production hostname points to the public IP associated with Traefik.

The production web service uses the `security-headers@file` middleware and is routed through Traefik using Docker labels.

## Development Deployment

Run from the repository root:

```bash
docker compose \
  -f compose/docker-compose.yml \
  -f compose/docker-compose.dev.yml \
  --env-file compose/.env.dev \
  --profile dev up
```

Alternatively, use the environment helper scripts:

```bash
./compose/up.sh dev
```

## UAT Deployment and Testing

Build the application image:

```bash
docker build -t meal_project:latest .
```

Start UAT:

```bash
./compose/up.sh uat
```

Run database migrations:

```bash
./compose/manage.sh uat migrate
```

To load a database fixture, copy it into the web container:

```bash
docker cp ../backup_meal_project_12242025.json \
  compose-web-1:/tmp/
```

Open a shell in the web container:

```bash
docker exec -it compose-web-1 bash
```

Inside the container:

```bash
python manage.py loaddata /tmp/backup_meal_project_12242025.json
python manage.py collectstatic
```

Test the application locally:

```text
http://127.0.0.1:8000/
```

When finished:

```bash
./compose/down.sh uat
```

## Production Deployment

Production deployment is performed on the production host.

Before starting:

1. Ensure `compose/.env.prod` exists and contains the production environment variables.
2. Ensure the standalone Traefik service is running.
3. Ensure the external Docker network `traefik_public` exists.
4. Confirm the production image reference in `compose/docker-compose.prod.yml` is correct.

Start the production services from the repository root:

```bash
docker compose \
  -f compose/docker-compose.yml \
  -f compose/docker-compose.prod.yml \
  --env-file compose/.env.prod \
  --profile prod \
  up -d
```

Check service status:

```bash
docker compose \
  -f compose/docker-compose.yml \
  -f compose/docker-compose.prod.yml \
  --env-file compose/.env.prod \
  --profile prod \
  ps
```

View application logs:

```bash
docker compose \
  -f compose/docker-compose.yml \
  -f compose/docker-compose.prod.yml \
  --env-file compose/.env.prod \
  --profile prod \
  logs -f web
```

Database logs:

```bash
docker logs myapp-db
```

## Database and Persistence

- PostgreSQL data is persisted in the Docker volume `pg_data`.
- The database is attached only to the private internal Docker network.
- The web service connects to the database over that internal network.
- The web service also connects to the external `traefik_public` network for reverse proxy access.
- PostgreSQL health is checked using `pg_isready`.

Back up the database regularly. Do not assume that a Docker volume alone is a backup.

**Important:** Avoid `docker compose down -v` in production. The `-v` option removes named volumes, including `pg_data`, and can permanently delete the production database.

## Production Go-Live Checklist

- [ ] Production environment file exists and contains valid secrets.
- [ ] Production image reference is correct.
- [ ] Standalone Traefik is running.
- [ ] External `traefik_public` network exists.
- [ ] Production hostname matches the Traefik router rule.
- [ ] DNS points to the production host.
- [ ] Database backup is current.
- [ ] Application and database containers start successfully.
- [ ] Application is accessible over HTTPS.

---

This document supplements `README.md` with deployment and operational instructions.
