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
  Refactor Meals project (split out ingredients)
  Make meal notes optional - DONE
  Add ingredient categories (i.e. produce/dairy/bread etc.)
  For cart items, add expandable bootstrap rows to show what meal an item came from
  Modify cart to be Week-based and not session-based, login still required
  Create an automated PROD deployment script (i.e. fabric/fabfile)
  a. Enhance...DB migrations
      python manage.py makemigrations
      python manage.py migrate
  b. 

