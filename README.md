
sudo touch /etc/config.json - old env properties

# New version
# containerized version

pre-requisite:
sudo apt-get install git python3-venv libffi-dev python3-dev libssl-dev python3-setuptools libjpeg8-dev zlib1g-dev libmysqlclient-dev
pip3 install wheel

1. Checkout the project:
  git clone https://github.com/sshoemake/Meal_Project.git
   Branch?? -b containerize_app

2. Cd to project directory: s/b meal_project

3.
  Build/Run Dev:
  docker-compose up --build
    -d for detached
    http://localhost:8000

  Build/Run Prod:
  docker-compose -f docker-compose.prod.yml up --build
    -d for detached
    http://localhost:1337


docker-compose down -v
docker-compose -f docker-compose.prod.yml logs -f

TODO: move to a "real" webserver (i.e. apache or uwsgi or nginx) - DONE (Gunicorn)
TDOO: env variables for deployment to different environments - DONE
TODO: letsencrypt certs

## TODO
1. Refactor Meals project (split out ingredients)
2. Add ingredient categories (i.e. produce/dairy/bread etc.)
3. For cart items, add expandable bootstrap rows to show what meal an item came from
4. Modify cart to be Week-based and not session-based, login still required
    a. date_list (-3, curr week, +3) - DONE
    b. selected_week - session variable that drives cart display and meal list
    c. meal_list - list of meals by day for the selected week
5. Create a Store project
    python manage.py startapp stores
    Item will be able to be linked to stores for aisle reference
6. Fix issue where default week is selected but cart qty and detail are out of sync
7. Add Shopping option on cart screen that will hide items as you put them in your real cart - Done
8. Deploy enhancements:
    Backup database from docker instance
    recycle mysql docker instance
9. create a docker to host the apache/wsgi instance (ngnx/gunicorn)