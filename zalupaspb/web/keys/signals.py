from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
import json
import logging
from .models import Key, KeyHistory

logger = logging.getLogger('keys')
channel_layer = get_channel_layer()

@receiver(post_save, sender=Key)
def key_post_save(sender, instance, created, **kwargs):
    """Сигнал после сохранения ключа"""
    if created:
        # Логируем создание ключа
        logger.info(f"Key {instance.key_code} created by {instance.created_by}")
        
        # Создаем запись в истории
        KeyHistory.objects.create(
            key=instance,
            action=KeyHistory.ActionType.CREATED,
            user=instance.created_by,
            details=f"Создан ключ типа {instance.get_key_type_display()} с длительностью {instance.duration_days} дней"
        )
        
        # Отправляем уведомление через WebSocket
        try:
            async_to_sync(channel_layer.group_send)(
                'key_status_updates',
                {
                    'type': 'key_status_update',
                    'key_id': str(instance.id),
                    'status': instance.status,
                    'action': 'created',
                    'timestamp': timezone.now().isoformat(),
                }
            )
        except Exception as e:
            logger.error(f"Error sending WebSocket notification: {e}")
    else:
        # Проверяем изменение статуса
        try:
            old_instance = Key.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                # Логируем изменение статуса
                logger.info(f"Key {instance.key_code} status changed from {old_instance.status} to {instance.status}")
                
                # Создаем соответствующую запись в истории
                action = None
                if instance.status == Key.KeyStatus.USED:
                    action = KeyHistory.ActionType.ACTIVATED
                    details = f"Ключ активирован пользователем {instance.activated_by}"
                elif instance.status == Key.KeyStatus.REVOKED:
                    action = KeyHistory.ActionType.REVOKED
                    details = "Ключ отозван"
                elif instance.status == Key.KeyStatus.EXPIRED:
                    action = KeyHistory.ActionType.EXPIRED
                    details = "Срок действия ключа истек"
                
                if action:
                    KeyHistory.objects.create(
                        key=instance,
                        action=action,
                        user=instance.activated_by if instance.status == Key.KeyStatus.USED else None,
                        details=details
                    )
                
                # Отправляем уведомление через WebSocket
                try:
                    async_to_sync(channel_layer.group_send)(
                        'key_status_updates',
                        {
                            'type': 'key_status_update',
                            'key_id': str(instance.id),
                            'status': instance.status,
                            'action': 'status_changed',
                            'timestamp': timezone.now().isoformat(),
                        }
                    )
                except Exception as e:
                    logger.error(f"Error sending WebSocket notification: {e}")
        except Key.DoesNotExist:
            pass 