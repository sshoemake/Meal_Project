
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
