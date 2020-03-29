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


## TODO
1. Add search to meal screen
2. Add "Add to cart" on ingredient detail screen
3. Modify "Add to cart" link on ingredient screen for items that are already in cart (maybe "Add++")
4. For cart items, add expandable bootstrap rows to show what meal an item came from
5. Modify cart to be Week-based and not session-based, login still required
6. Create an automated PROD deployment script (i.e. fabric/fabfile)
   a. Backup mysql DB
   b. Git deploy (PROD Deploy - git pull origin master --force)
   c. Load virtual environment
   d. install pip items
   e. restart Apache2

