
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

## Docker and Compose commands:
##
docker-compose down -v # -v = volume, deletes data!!
docker-compose -f docker-compose.prod.yml logs -f


## manually load database from sql dump
# Find running container for mysql:
>docker container ls

# get the container id (use in fabric later)
sudo docker ps -aqf "name=^meal_project_db_1$"

## load database
>sudo docker exec -i [container_id] sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD" meal_project' < ./meal_project_[date].sql

## Backup Database
>sudo docker exec -i [container_id] sh -c 'exec mysqldump -u root -p"$MYSQL_ROOT_PASSWORD" meal_project' > ~/mysql_backups/meal_project_[date].sql
--OR--
>sudo docker exec -i `sudo docker ps -aqf "name=^meal_project-db-1$"` sh -c 'exec mysqldump -u root -p"$MYSQL_ROOT_PASSWORD" meal_project' > ~/mysql_backups/meal_project_`date +"%Y_%m_%d_%I_%M_%p"`.sql
  (onserver - meal_project_db_1$)

TODO: Move certbot certs to a volume
TODO: Database env properties
TODO: Meal history (on Meal Detail screen)
TODO: switch db from MySQL to PostgreSQL

## TODO
1. Add ingredient categories (i.e. produce/dairy/bread etc.)
2. For cart items, add expandable bootstrap rows to show what meal an item came from
3. Modify cart to be Week-based and not session-based, login still required
    a. date_list (-3, curr week, +3) - DONE
    b. selected_week - session variable that drives cart display and meal list
    c. meal_list - list of meals by day for the selected week
4. Create a Store project
    python manage.py startapp stores - DONE
    Item will be able to be linked to stores for aisle reference - In Progress
    Use docker dashboard to attach to mysql and run the following commands:
    mysql -uroot -p"$MYSQL_ROOT_PASSWORD" meal_project
    update query:
    insert into ingredients_ing_store (ingredient_id, aisle, store_id) 
    select id, aisle, '1' from ingredients_ingredient;
    
5. Fix issue where default week is selected but cart qty and detail are out of sync
6. Deploy enhancements:
    Backup database from docker instance - DONE
    recycle mysql docker instance
7. add a "return to default" button for meal image
8. Fix issue with uploading image error
9. Add API interface to support future Siri integration
10. Allow users to update their password
11. setup dockerized phpMyAdmin
    https://towardsdatascience.com/connect-to-mysql-running-in-docker-container-from-a-local-machine-6d996c574e55
