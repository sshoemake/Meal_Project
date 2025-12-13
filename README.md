
# Meal Project

Django based application for shopping and meal planning.

## Tech Stack

- **Language:** Python 3 (development and runtime)
- **Framework:** Django (server-side web framework)
- **Database:** PostgreSQL 15 (containerized)
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
  python3 -m venv venv
  source venv/bin/activate

4. Install required packages
  python -m pip install --upgrade pip
  pip install -r requirements.txt

5. Startup/Create database in docker
  ~~docker compose up -d~~
  docker compose -f compose/docker-compose.yml \
    -f compose/docker-compose.dev.yml \
    --env-file compose/.env.dev \
    --profile dev up -d

  python manage.py migrate

  python manage.py createsuperuser
  or
  python manage.py loaddata data_dump.json

  python manage.py collectstatic

  python manage.py runserver

  http://127.0.0.1:8000/


# pgAdmin
  http://localhost:8080/browser/
  Login = admin@example.com
  Add New Server
  Connection -> Host Name/address = my_postgres_db
  Username = myuser


# Import data (store)
  insert into public.stores_store ("name", "address", "city", "state", "zip_code", "default")
  values ('Albertsons', 'address', 'city', 'AZ', '95829', true)


# blow away database and data:
  docker compose down -v

# Delete a Virtual Environment
  deactivate
  rm -rf venv

# Run tests
  python manage.py test

# Build and test Docker image
  docker build -t meal_project:latest .

  docker run --rm -it -p 8000:8000 -v "$(pwd)/db:/app/db" -e DEBUG=1 meal_project:latest