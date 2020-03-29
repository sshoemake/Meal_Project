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

    c.run(
        "mysqldump -u root -p'"
        + sudo_pass
        + "' meal_project > meal_project_"
        + timestr
        + ".sql"
    )

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

    c.sudo("service apache2 restart")
