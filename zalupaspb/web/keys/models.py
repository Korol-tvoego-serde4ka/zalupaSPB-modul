from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
import uuid
import string
import random


class Key(models.Model):
    """Модель ключа доступа к сервисам"""
    
    class KeyType(models.TextChoices):
        STANDARD = 'standard', _('Стандартный')
        PREMIUM = 'premium', _('Премиум')
        LIFETIME = 'lifetime', _('Пожизненный')
    
    class KeyStatus(models.TextChoices):
        ACTIVE = 'active', _('Активный')
        USED = 'used', _('Использован')
        EXPIRED = 'expired', _('Истёк')
        REVOKED = 'revoked', _('Отозван')
    
    # Основная информация
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=36, unique=True, verbose_name=_('Ключ'))
    key_type = models.CharField(
        max_length=20,
        choices=KeyType.choices,
        default=KeyType.STANDARD,
        verbose_name=_('Тип ключа')
    )
    status = models.CharField(
        max_length=20,
        choices=KeyStatus.choices,
        default=KeyStatus.ACTIVE,
        verbose_name=_('Статус')
    )
    
    # Информация о создании и активации
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_keys',
        verbose_name=_('Создан пользователем')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    activated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activated_keys',
        verbose_name=_('Активирован пользователем')
    )
    activated_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Дата активации'))
    
    # Сроки действия
    duration_days = models.IntegerField(default=30, verbose_name=_('Длительность (дней)'))
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Дата истечения'))
    
    # Дополнительная информация
    notes = models.TextField(blank=True, null=True, verbose_name=_('Примечания'))
    
    class Meta:
        verbose_name = _('Ключ')
        verbose_name_plural = _('Ключи')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.key} ({self.get_key_type_display()})"
    
    def save(self, *args, **kwargs):
        # Генерируем ключ, если он еще не создан
        if not self.key:
            self.key = self.generate_key()
        
        # Для пожизненных ключей не устанавливаем дату истечения
        if self.key_type == self.KeyType.LIFETIME:
            self.expires_at = None
        # Если ключ был активирован, устанавливаем дату истечения
        elif self.activated_at and not self.expires_at:
            self.expires_at = self.activated_at + timezone.timedelta(days=self.duration_days)
        
        super().save(*args, **kwargs)
    
    def activate(self, user):
        """Активация ключа пользователем"""
        if self.status != self.KeyStatus.ACTIVE:
            return False
        
        self.activated_by = user
        self.activated_at = timezone.now()
        self.status = self.KeyStatus.USED
        self.save()
        return True
    
    def revoke(self):
        """Отзыв ключа"""
        self.status = self.KeyStatus.REVOKED
        self.save()
        return True
    
    def check_expiry(self):
        """Проверка истечения срока ключа"""
        if self.status == self.KeyStatus.ACTIVE or self.status == self.KeyStatus.USED:
            if self.expires_at and timezone.now() > self.expires_at:
                self.status = self.KeyStatus.EXPIRED
                self.save()
        return self.status
    
    @property
    def is_active(self):
        """Проверка активности ключа"""
        self.check_expiry()
        return self.status == self.KeyStatus.ACTIVE
    
    @property
    def is_valid(self):
        """Проверка валидности ключа (активен или использован и не истек)"""
        self.check_expiry()
        return self.status in [self.KeyStatus.ACTIVE, self.KeyStatus.USED]
    
    @property
    def remaining_days(self):
        """Оставшееся количество дней действия ключа"""
        if self.key_type == self.KeyType.LIFETIME:
            return float('inf')
        if not self.expires_at:
            return 0
        
        delta = self.expires_at - timezone.now()
        return max(0, delta.days)
    
    @classmethod
    def generate_key(cls):
        """Генерация уникального ключа"""
        while True:
            key = f"{uuid.uuid4()}"
            if not cls.objects.filter(key=key).exists():
                return key


class KeyHistory(models.Model):
    """История действий с ключом"""
    
    class ActionType(models.TextChoices):
        CREATED = 'created', _('Создан')
        ACTIVATED = 'activated', _('Активирован')
        REVOKED = 'revoked', _('Отозван')
        EXPIRED = 'expired', _('Истёк')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.ForeignKey(Key, on_delete=models.CASCADE, related_name='history', verbose_name=_('Ключ'))
    action = models.CharField(max_length=20, choices=ActionType.choices, verbose_name=_('Действие'))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='key_actions',
        verbose_name=_('Пользователь')
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата и время'))
    details = models.TextField(blank=True, null=True, verbose_name=_('Детали'))
    
    class Meta:
        verbose_name = _('История ключа')
        verbose_name_plural = _('История ключей')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.key} - {self.get_action_display()}" 