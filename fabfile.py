import getpass
import time
from fabric import task, Connection, Config

REPO_URL = "https://github.com/sshoemake/Meal_Project.git"


@task
def deploy(ctx):
    timestr = time.strftime("%Y%m%d-%H%M%S")
    # print("Hello world!")

    sudo_pass = getpass.getpass("What's your sudo password?")
    config = Config(overrides={"sudo": {"password": sudo_pass}})
    c = Connection("odroid@odroidn2.local", config=config)

    # c.run(
    #     "mysqldump -u root -p'"
    #     + sudo_pass
    #     + "' meal_project > ~/mysql_backups/meal_project_"
    #     + timestr
    #     + ".sql"
    # )

    c.sudo(
        "docker exec mysql mysqldump -u root -p'"
        + sudo_pass
        + "' meal_project > ~/mysql_backups/meal_project_"
        + timestr
        + ".sql"
    )

    ## from mysql docker site:
    ##$ docker exec some-mysql sh -c 'exec mysqldump --all-databases -uroot -p"$MYSQL_ROOT_PASSWORD"' > /some/path/on/your/host/all-databases.sql


    site_folder = "/home/odroid/meal_project"
    c.run(f"mkdir -p {site_folder}")

    # current_commit = c.local("HOME=~ git log -n 1 --format=%H")
    with c.cd(site_folder):
        if c.run("test -d .git", warn=True).failed:
            c.run(f"git clone {REPO_URL} .")
        else:
            # c.run("git pull origin master --force")
            c.run("git fetch")
        c.run("git reset --hard origin/master")

        # PIP load from requirements.txt
        venv_command = "source venv/bin/activate"
        pip_command = "venv/bin/pip3 install -r requirements.txt"
        c.run(venv_command + " && " + pip_command)

        # Reload static files
        static_cmd = "python manage.py collectstatic --noinput"
        c.run(venv_command + " && " + static_cmd)

        # Database Make Migration
        makem_cmd = "python manage.py makemigrations --settings=meal_project.settings.production"
        c.run(venv_command + " && " + makem_cmd)

        # Database Migrate
        migrate_cmd = (
            "python manage.py migrate --settings=meal_project.settings.production"
        )
        c.run(venv_command + " && " + migrate_cmd)

    # Restart Apache
    c.sudo("service apache2 restart")


@task
def backup_db(ctx):
    ## must call with fab backup-db
    ##
    timestr = time.strftime("%Y%m%d-%H%M%S")
    # print("Hello world!")

    sudo_pass = getpass.getpass("What's your sudo password?")
    config = Config(overrides={"sudo": {"password": sudo_pass}})
    c = Connection("odroid@odroidn2.local", config=config)

    # c.run(
    #     "mysqldump -u root -p'"
    #     + sudo_pass
    #     + "' meal_project > ~/mysql_backups/meal_project_"
    #     + timestr
    #     + ".sql"
    # )

    c.sudo(
        "docker exec mysql mysqldump -u root -p'"
        + sudo_pass
        + "' meal_project > ~/mysql_backups/meal_project_"
        + timestr
        + ".sql"
    )
