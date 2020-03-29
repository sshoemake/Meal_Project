import getpass
import time

# from fabric.contrib.files import exists
from fabric import task, Connection, Config

# from fabric.api import cd, env, local, run

REPO_URL = "https://github.com/sshoemake/Meal_Project.git"


@task
def deploy(ctx):
    timestr = time.strftime("%Y%m%d-%H%M%S")
    # print("Hello world!")

    sudo_pass = getpass.getpass("What's your sudo password?")
    config = Config(overrides={"sudo": {"password": sudo_pass}})
    c = Connection("odroid@odroidn2.local", config=config)
    result = c.run("uname -s")
    # print(result)

    # whoami = c.sudo("whoami", hide="stderr")
    # print(whoami)

    c.run(
        "mysqldump -u root -p'"
        + sudo_pass
        + "' meal_project > meal_project_"
        + timestr
        + ".sql"
    )

    site_folder = f"/home/odroid/meal_project"
    c.run(f"mkdir -p {site_folder}")
    with c.cd(site_folder):
        if c.run("test -d .git", warn=True).failed:
            c.run(f"git clone {REPO_URL} .")
        else:
            c.run("git fetch")
        current_commit = c.local("git log -n 1 --format=%H", capture=True)
        c.run(f"git reset --hard {current_commit}")


#        if files.exists(".git"):
#            c.run("git fetch")
#        else:
#            run(f"git clone {REPO_URL} .")
#        current_commit = local("git log -n 1 --format=%H", capture=True)
#        run(f"git reset --hard {current_commit}")
