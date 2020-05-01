# Meal_Project

1. Checkout the project:
  git clone https://github.com/sshoemake/Meal_Project.git

2. Cd to project directory:

3. Create a Virtual Environment:
  python3 -m venv venv

4. Activate the Virtual Env.
  source ./venv/bin/activate

5. Install Packages
  pip3 install -r requirements.txt

6. Run the Project:
  python manage.py runserver

# Deploy to linux server:
# run under apache & mysql

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

TEST site using sqlite3 database
#need to add steps to install and configure mysql db


## TODO
1. Refactor Meals project (split out ingredients)
2. Add ingredient categories (i.e. produce/dairy/bread etc.)
3. For cart items, add expandable bootstrap rows to show what meal an item came from
4. Modify cart to be Week-based and not session-based, login still required
    a. date_list (-3, curr week, +3) - DONE
    b. selected_week - session variable that drives cart display and meal list
    c. meal_list - list of meals by day for the selected week
