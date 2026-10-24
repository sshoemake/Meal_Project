
# Meal Project

Django based application for shopping and meal planning.

## Tech Stack

- **Language:** Python 3 (development and runtime)
- **Framework:** Django (server-side web framework)
- **Database:** PostgreSQL 18 (containerized)
- **Reverse proxy & TLS:** Traefik v3 (LetsEncrypt/ACME via `acme.json`)
- **Containerization:** Docker, Docker Compose
- **Container registry:** GitHub Container Registry (ghcr.io) (used in compose)
- **Frontend:** Django templates with static CSS/JS
- **Testing:** Django test runner (`python manage.py test`)
- **Packaging & deps:** pip, `requirements.txt`, virtualenv


# Build and Deployment

1. Checkout the project:
  git clone https://github.com/sshoemake/Meal_Project.git

2. Cd to project directory: i.e. cd Meal_Project

3. Create Virtual Environment

  ```bash
  python3.12 -m venv venv
  source venv/bin/activate
  ```

4. Install required packages

  ```bash
  python -m pip install --upgrade pip
  pip install -r requirements-dev.txt
  ```

5. Startup/Create database in docker

  ```bash
  ./compose/up.sh dev
  ```

6. Database migrations

  ```bash
  ./compose/manage.sh dev migrate
  ```

7. Misc

  ```bash
  ./compose/manage.sh dev loaddata ../backup_meal_project_12242025.json

  ./compose/manage.sh dev collectstatic
  ```

8. Start Application

  ```bash
  ./compose/manage.sh dev runserver

  http://127.0.0.1:8000/
  ```

# pgAdmin

  ```bash
  http://localhost:8080/browser/
  Login = admin@example.com
  Add New Server
  Connection -> Host Name/address = my_postgres_db
  Username = myuser
  ```

# blow away database and data:
  
  ```bash
  ./compose/down.sh dev -v
  ```

# Delete a Virtual Environment

  ```bash
  deactivate
  rm -rf venv
  ```

# Run tests
  
  ```bash
  python manage.py test
  python manage.py check
  python manage.py shell
  ```

# Deploy/config checks (mirrors CI)

Runs Django's deployment checklist against the production settings so you can
catch issues locally before they fail the `Deploy checks` step in CI. The
throwaway secret key is generated per-run — the check validates the config
shape, not your real key.

  ```bash
  DJANGO_SETTINGS_MODULE=app.meal_project.settings.prod \
  DJANGO_SECRET_KEY="$(openssl rand -hex 32)" \
  DJANGO_ALLOWED_HOSTS=sshoemake.com \
  DJANGO_CSRF_TRUSTED_ORIGINS=sshoemake.com \
  python manage.py check --deploy --fail-level WARNING
  ```

The security settings it verifies are env-overridable with secure defaults in
`app/meal_project/settings/prod.py` (see the `DJANGO_*` variables there), e.g.
`DJANGO_DEBUG`, `DJANGO_SESSION_COOKIE_SECURE`,
`DJANGO_SECURE_SSL_REDIRECT`, `DJANGO_SECURE_HSTS_SECONDS`.

# How to release

Releases are automatic — merge into `main` any PR carrying a version label and
the release workflow builds and pushes the Docker image, then creates the
release tag and GitHub Release.

Label → version bump (from the latest `vX.Y.Z` tag):

  ```text
  major  →  v3.0.0
  minor  →  v2.3.0
  patch  →  v2.2.5
  ```

Rules:

- A merged PR with **no** version label does not trigger a release.
- If multiple version labels are present, `major` wins over `minor` over `patch`.
- CI checks (lint, tests, coverage, deploy checks) run before a release is created.

Steps:

1. Create the labels once (repo Settings → Labels, or the CLI):
   `gh label create major && gh label create minor && gh label create patch`
2. Open a PR to `main` from your feature branch and add the matching label
   (`patch` for a fix, `minor` for a feature, `major` for breaking changes).
3. Merge the PR. Checks run, the image is pushed, and the tag + Release are
   created automatically.

Deploying to the host (e.g. `docker compose pull && docker compose up -d`) is
still a manual step.

# Run Linting

  ```bash
  ruff check .
  ```

# Test Coverage

  ```bash
  coverage run manage.py test
  coverage html
  Open in Browser: htmlcov/index.html
  ```

# Product Backlog

Link weekly meals to days of the week
API Token associated to registered User
API to add ingredients to shopping list
