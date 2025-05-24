from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import uuid


class Log(models.Model):
    """Модель для хранения логов системы"""
    
    class LogLevel(models.TextChoices):
        DEBUG = 'debug', _('Отладка')
        INFO = 'info', _('Информация')
        WARNING = 'warning', _('Предупреждение')
        ERROR = 'error', _('Ошибка')
        CRITICAL = 'critical', _('Критическая ошибка')
    
    class LogCategory(models.TextChoices):
        USER = 'user', _('Пользователи')
        KEY = 'key', _('Ключи')
        INVITE = 'invite', _('Инвайты')
        DISCORD = 'discord', _('Discord')
        SYSTEM = 'system', _('Система')
        SECURITY = 'security', _('Безопасность')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата и время'))
    level = models.CharField(
        max_length=10,
        choices=LogLevel.choices,
        default=LogLevel.INFO,
        verbose_name=_('Уровень')
    )
    category = models.CharField(
        max_length=20,
        choices=LogCategory.choices,
        default=LogCategory.SYSTEM,
        verbose_name=_('Категория')
    )
    message = models.TextField(verbose_name=_('Сообщение'))
    
    # Связь с пользователем (если действие выполнено пользователем)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs',
        verbose_name=_('Пользователь')
    )
    
    # IP адрес
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name=_('IP адрес'))
    
    # Дополнительные данные в формате JSON
    extra_data = models.JSONField(null=True, blank=True, verbose_name=_('Дополнительные данные'))
    
    class Meta:
        verbose_name = _('Лог')
        verbose_name_plural = _('Логи')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.timestamp} [{self.get_level_display()}] {self.message[:50]}..." 