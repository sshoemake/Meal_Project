import getpass
from fabric import task, Connection, Config

@task
def hello(ctx):
    print("Hello world!")

    sudo_pass = getpass.getpass("What's your sudo password?")
    config = Config(overrides={'sudo': {'password': sudo_pass}})
    c = Connection('odroid@odroidn2.local', config=config)
    result = c.run('uname -s')
    print(result)

    whoami = c.sudo('whoami', hide='stderr')
    print(whoami)

    c.run("mysqldump -u root -p'"+sudo_pass + "' meal_project > meal_project.sql")

