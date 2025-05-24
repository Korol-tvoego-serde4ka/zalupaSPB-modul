from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import logging
from .models import Invite

logger = logging.getLogger('invites')

@receiver(post_save, sender=Invite)
def invite_post_save(sender, instance, created, **kwargs):
    """Сигнал после сохранения инвайта"""
    if created:
        # Логируем создание инвайта
        logger.info(f"Invite {instance.code} created by {instance.created_by.username}")
    else:
        # Проверяем изменение статуса
        try:
            old_instance = Invite.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                # Логируем изменение статуса
                logger.info(f"Invite {instance.code} status changed from {old_instance.status} to {instance.status}")
                
                # Дополнительная логика при использовании инвайта
                if instance.status == Invite.InviteStatus.USED and instance.used_by:
                    logger.info(f"Invite {instance.code} used by {instance.used_by.username}")
        except Invite.DoesNotExist:
            pass 