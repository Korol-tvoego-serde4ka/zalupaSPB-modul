from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import User
from django.conf import settings
import logging

logger = logging.getLogger('users')

@receiver(pre_save, sender=User)
def user_pre_save(sender, instance, **kwargs):
    """Сигнал до сохранения пользователя"""
    if instance.pk:
        try:
            old_instance = User.objects.get(pk=instance.pk)
            # Если роль пользователя изменилась, обновляем лимиты инвайтов вручную
            if old_instance.role != instance.role:
                if instance.role in settings.INVITE_LIMITS:
                    instance.monthly_invites_limit = settings.INVITE_LIMITS[instance.role]
                
                # Логируем изменение роли
                logger.info(f"User {instance.username} role changed from {old_instance.role} to {instance.role}")
                
                # Здесь будет вызов асинхронной задачи для обновления ролей в Discord
                # После создания Celery tasks
                # from .tasks import sync_discord_roles
                # sync_discord_roles.delay(instance.id)
        except User.DoesNotExist:
            pass

@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """Сигнал после сохранения пользователя"""
    if created:
        # Устанавливаем лимиты инвайтов для нового пользователя
        if instance.role in settings.INVITE_LIMITS:
            # Если пользователь только что создан, обновляем лимиты напрямую
            monthly_limit = settings.INVITE_LIMITS[instance.role]
            User.objects.filter(pk=instance.pk).update(monthly_invites_limit=monthly_limit)
        
        logger.info(f"User {instance.username} created with role {instance.role}")
    
    # Если пользователь был забанен, здесь можно добавить дополнительную логику
    if instance.is_banned:
        logger.warning(f"User {instance.username} was banned. Reason: {instance.ban_reason}")
        # Здесь будет вызов асинхронной задачи для обновления ролей в Discord
        # После создания Celery tasks 