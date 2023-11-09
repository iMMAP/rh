from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
    verbose_name = "Profiles"

    def ready(self):
        # ruff: noqa
        import users.signals
