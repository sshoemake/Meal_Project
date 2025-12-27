
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
  pip install -r requirements.txt
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
  ./compose/manage.sh dev loaddata data_dump.json

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

# Import data (store)
  insert into public.stores_store ("name", "address", "city", "state", "zip_code", "default")
  values ('Albertsons', 'address', 'city', 'AZ', '95829', true)


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
  ```

# Build and test Docker image in UAT

  ```bash
  docker build -t meal_project:latest .
  ./compose/up.sh uat
  ./compose/manage.sh uat migrate
  docker cp ../backup_meal_project_12242025.json compose-web-1:/tmp/
  open command line in web container
  python manage.py loaddata /tmp/data_dump.json
  ./compose/down.sh uat
  ```