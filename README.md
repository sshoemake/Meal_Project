
# Meal Project

Django based application for shopping and meal planning.

# Build and Deployment

1. Checkout the project:
  git clone https://github.com/sshoemake/Meal_Project.git

2. Cd to project directory: i.e. cd Meal_Project

3. Create Virtual Environment
  python3 -m venv venv
  source venv/bin/activate

4. Install required packages
  pip install --upgrade pip
  pip install -r requirements.txt

5. Startup/Create database in docker
  docker compose up -d

  python manage.py migrate
  python manage.py createsuperuser

  python manage.py runserver

  http://127.0.0.1:8000/


# pgAdmin
  http://localhost:8080/browser/
  Login = admin@example.com
  Add New Server
  Connection -> Host Name/address = my_postgres_db
  Username = myuser


# Import data
  insert into public.stores_store ("name", "address", "city", "state", "zip_code", "default")
  values ('Albertsons', 'address', 'city', 'AZ', '95829', true)

  Import old mysql data (not working):
  python manage.py sqlflush | python manage.py dbshell - skipped
  python manage.py loaddata contenttype.json
  python manage.py loaddata everything_else.json (ran twice)


# blow away database and data:
  docker compose down -v

# Delete a Virtual Environment
  deactivate

  rm -rf venv

# Run tests
  python manage.py test
