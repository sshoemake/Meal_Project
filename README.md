
# Meal Project

Django based application for shopping and meal planning.

# Build and Deployment

pre-requisite:
sudo apt-get install git python3-venv libffi-dev python3-dev libssl-dev python3-setuptools libjpeg8-dev zlib1g-dev libmysqlclient-dev python3-pip docker-compose
pip3 install wheel

1. Checkout the project:
  git clone https://github.com/sshoemake/Meal_Project.git

2. Cd to project directory: i.e. cd Meal_Project

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

docker compose up -d

python manage.py migrate
python manage.py createsuperuser

http://localhost:8080/browser/

insert into public.stores_store ("name", "address", "city", "state", "zip_code", "default")
values ('Albertsons', 'address', 'city', 'AZ', '95829', true)

python manage.py runserver

Import old mysql data (not working):
python manage.py sqlflush | python manage.py dbshell
python manage.py loaddata contenttype.json
python manage.py loaddata everything_else.json




blow away database and data:
  docker compose down -v

Run tests
python manage.py test


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

## TODO
1. Add ingredient categories (i.e. produce/dairy/bread etc.)
2. For cart items, add expandable bootstrap rows to show what meal an item came from
3. Modify cart to be Week-based and not session-based, login still required
    a. date_list (-3, curr week, +3) - DONE
    b. selected_week - session variable that drives cart display and meal list
    c. meal_list - list of meals by day for the selected week
4. Meals, update model and UI to support Quantity value for Ingredient items
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
12. Move certbot certs to a volume
13. Database env properties
14. switch db from MySQL to PostgreSQL