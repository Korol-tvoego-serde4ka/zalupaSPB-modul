from django.apps import AppConfig


class LogsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'logs'
    verbose_name = 'Логи'
    
    def ready(self):
        # Импортируем сигналы при инициализации приложения
        import logs.signals 