from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'app.users'

    def ready(self):
        # Import signals to register them
        import app.users.signals  # noqa: F401
