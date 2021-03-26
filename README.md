
# New version
# containerized version

pre-requisite:
sudo apt-get install git python3-venv libffi-dev python3-dev libssl-dev python3-setuptools libjpeg8-dev zlib1g-dev libmysqlclient-dev
pip3 install wheel

1. Checkout the project:
  git clone https://github.com/sshoemake/Meal_Project.git

2. Cd to project directory: s/b Meal_Project

3a. Build/Run Dev:
  docker-compose up --build
    -d for detached
    http://localhost:8000

3b. Build/Run Prod:
  docker-compose -f docker-compose.prod.yml up --build
    -d for detached
    http://localhost


docker-compose down -v
docker-compose -f docker-compose.prod.yml logs -f


## manually load database from sql dump
Find running container for mysql:
>docker container ls

>docker exec -i [container_id] sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD" meal_project' < ./meal_project_[date].sql


TODO: Move certbot certs to a volume
TODO: Database env properties

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
9. add a "return to default" button for meal image
10. Fix issue with uploading image error
