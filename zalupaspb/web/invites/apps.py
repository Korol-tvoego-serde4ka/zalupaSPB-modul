from django.apps import AppConfig


class InvitesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'invites'
    verbose_name = 'Инвайты'

    def ready(self):
        import invites.signals 