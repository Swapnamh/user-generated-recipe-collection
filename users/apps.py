from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    #label = 'my_users'  # Unique label to avoid conflicts

    def ready(self):
        import users.signals 