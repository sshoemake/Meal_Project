# Meal_Project

pre-requisite:
sudo apt-get install git python3-venv libffi-dev python3-dev libssl-dev python3-setuptools libjpeg8-dev zlib1g-dev libmysqlclient-dev build-essential
pip3 install wheel (failed, worked as step 4.5)

1. Checkout the project:
  git clone https://github.com/sshoemake/Meal_Project.git

2. Cd to project directory: s/b meal_project

3. Create a Virtual Environment:
  python3 -m venv venv

4. Activate the Virtual Env.
  source ./venv/bin/activate

5. Install Packages
  pip3 install -r requirements.txt


python manage.py collectstatic

IF Local:
6. Run the Project:
  python manage.py runserver

IF Server:
# Deploy to linux server:
# run under apache & mysql

sudo apt-get update
sudo apt-get install mysql-server
sudo systemctl status mysql
sudo mysql_secure_installation
#load data
  sudo mysql
  create database meal_project;
  exit;
  sudo mysql meal_project < meal_project_20200501-132836.sql


sudo apt-get install apache2
sudo apt-get install libapache2-mod-wsgi-py3

cd /etc/apache2/sites-available
sudo cp 000-default.conf meal_project.conf
sudo vi meal_project.conf
Add this before the closing </VirtualHost>:

	Alias /static /home/odroid/meal_project/static
	<Directory /home/odroid/meal_project/static>
		Require all granted
	</Directory>

        Alias /media /home/odroid/meal_project/media
        <Directory /home/odroid/meal_project/media>
                Require all granted
        </Directory>

	<Directory /home/odroid/meal_project/meal_project>
		<Files production_wsgi.py>
			Require all granted
		</Files>
	</Directory>

	WSGIScriptAlias / /home/odroid/meal_project/meal_project/production_wsgi.py
	WSGIDaemonProcess meal_app python-path=/home/odroid/meal_project python-home=/home/odroid/meal_project/venv
	WSGIProcessGroup meal_app

sudo a2ensite meal_project
sudo a2dissite 000-default.conf

sudo chown :www-data meal_project/db.sqlite3
sudo chmod 664 meal_project/db.sqlite3

sudo chown :www-data meal_project/
sudo chmod 775 meal_project/

sudo chown -R :www-data meal_project/media/
sudo chmod -R 775 meal_project/media

sudo touch /etc/config.json

  {
    "SECRET_KEY": "",
    "EMAIL_USER": "",
    "EMAIL_PASS": "",
    "ROOT_PASS": ""
  }

sudo service apache2 restart


#TEST site using sqlite3 database
python manage.py runserver 0.0.0.0:8000 --settings=meal_project.settings.production
Had to install mysqlclient on linux
#Had an access issue to the database
sudo mysql
grant all privileges on meal_project.* to root@localhost;
exit;

sudo mysql
mysql> USE mysql;
mysql> UPDATE user SET plugin='mysql_native_password' WHERE User='root';
mysql> FLUSH PRIVILEGES;
mysql> exit;

$ sudo service mysql restart

mysql -u root
ALTER USER 'root'@'localhost' IDENTIFIED BY 'PASSWORD';
exit;
$ sudo service mysql restart

## DEPLOYMENT ##
from command line type: "fab deploy"

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
7. Add Shopping option on cart screen that will hide items as you put them in your real cart
8. Deploy enhancements:
    Backup database from docker instance
    recycle mysql docker instance
9. create a docker to host the apache/wsgi instance


installed on server | requirements.txt:
mysqlclient==1.4.6					      |	#mysqlclient==1.4.6
pkg-resources==0.0.0					      |	#pkg-resources==0.0.0
