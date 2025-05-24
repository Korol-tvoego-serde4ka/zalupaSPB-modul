from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Log

@receiver(post_save, sender=Log)
def clean_old_logs(sender, instance, **kwargs):
    """
    Оставляет только 5 последних логов для каждого пользователя и категории.
    Для системных логов (без пользователя) также оставляет только 5 последних по каждой категории.
    """
    if instance.user:
        # Получаем все логи данного пользователя и категории, отсортированные по времени (новые в начале)
        user_logs = Log.objects.filter(
            user=instance.user, 
            category=instance.category
        ).order_by('-timestamp')
        
        # Если логов больше 5, удаляем лишние
        if user_logs.count() > 5:
            logs_to_delete = user_logs[5:]
            for log in logs_to_delete:
                log.delete()
    else:
        # Для системных логов (без пользователя) по каждой категории
        system_logs = Log.objects.filter(
            user=None,
            category=instance.category
        ).order_by('-timestamp')
        
        # Если логов больше 5, удаляем лишние
        if system_logs.count() > 5:
            logs_to_delete = system_logs[5:]
            for log in logs_to_delete:
                log.delete() 