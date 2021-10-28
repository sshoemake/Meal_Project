
# New version
# containerized version

pre-requisite:
sudo apt-get install git python3-venv libffi-dev python3-dev libssl-dev python3-setuptools libjpeg8-dev zlib1g-dev libmysqlclient-dev python3-pip docker-compose
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


# -v = volume, deletes data!!
docker-compose down -v
docker-compose -f docker-compose.prod.yml logs -f


## manually load database from sql dump
Find running container for mysql:
>docker container ls

# get the container id (use in fabric later)
sudo docker ps -aqf "name=^meal_project_db_1$"

## load database
>docker exec -i [container_id] sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD" meal_project' < ./meal_project_[date].sql

## Backup Database
>sudo docker exec -i [container_id] sh -c 'exec mysqldump -u root -p"$MYSQL_ROOT_PASSWORD" meal_project' > ~/mysql_backups/meal_project_[date].sql
--OR--
>sudo docker exec -i `sudo docker ps -aqf "name=^meal_project-db-1$"` sh -c 'exec mysqldump -u root -p"$MYSQL_ROOT_PASSWORD" meal_project' > ~/mysql_backups/meal_project_`date +"%Y_%m_%d_%I_%M_%p"`.sql


TODO: Move certbot certs to a volume
TODO: Database env properties
TODO: Meal history (on Meal Detail screen)
TODO: switch db from MySQL to PostgreSQL

## TODO
1. Refactor Meals project (split out ingredients)
  - migration, update sql export:
    meals_ingredient -> ingredients_ingredient
    :%s/meals_ingredient/ingredients_ingredient/g
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
7. Deploy enhancements:
    Backup database from docker instance
    recycle mysql docker instance
8. add a "return to default" button for meal image
9. Fix issue with uploading image error
10. Add API interface to support future Siri integration
