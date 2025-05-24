from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
import uuid


class User(AbstractUser):
    """Модель пользователя с расширенными полями для интеграции с Discord"""
    
    class Role(models.TextChoices):
        ADMIN = 'admin', _('Администратор')
        MODERATOR = 'moderator', _('Модератор')
        SUPPORT = 'support', _('Поддержка')
        USER = 'user', _('Пользователь')

    # Основные поля
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(
        max_length=20, 
        choices=Role.choices,
        default=Role.USER,
        verbose_name=_('Роль')
    )
    is_banned = models.BooleanField(default=False, verbose_name=_('Заблокирован'))
    ban_reason = models.TextField(blank=True, null=True, verbose_name=_('Причина блокировки'))
    
    # Поля для Discord
    discord_id = models.CharField(max_length=50, blank=True, null=True, unique=True, verbose_name=_('Discord ID'))
    discord_username = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Discord имя пользователя'))
    discord_avatar = models.URLField(blank=True, null=True, verbose_name=_('Discord аватар'))
    
    # Информация о регистрации
    registered_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name=_('IP при регистрации'))
    invited_by = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True, 
        related_name='invited_users',
        verbose_name=_('Приглашен пользователем')
    )
    
    # Лимиты инвайтов
    monthly_invites_limit = models.IntegerField(default=2, verbose_name=_('Лимит инвайтов в месяц'))
    invites_used_this_month = models.IntegerField(default=0, verbose_name=_('Использовано инвайтов в этом месяце'))
    last_invite_reset = models.DateTimeField(default=timezone.now, verbose_name=_('Последний сброс инвайтов'))
    
    # Дополнительная информация
    last_login_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name=_('IP последнего входа'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('Примечания'))
    
    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
    
    def __str__(self):
        return self.username
    
    def get_invites_available(self):
        """Возвращает количество доступных инвайтов"""
        if self.role == self.Role.ADMIN:
            return float('inf')  # Бесконечно для админов
        
        # Проверка, нужно ли сбросить счетчик инвайтов (прошел месяц)
        now = timezone.now()
        month_ago = now - timezone.timedelta(days=30)
        
        if self.last_invite_reset < month_ago:
            # Сбрасываем счетчик
            self.invites_used_this_month = 0
            self.last_invite_reset = now
            self.save(update_fields=['invites_used_this_month', 'last_invite_reset'])
        
        return max(0, self.monthly_invites_limit - self.invites_used_this_month)
    
    def get_discord_roles(self):
        """Возвращает список ID ролей Discord для данного пользователя"""
        if not self.discord_id:
            return []
        
        roles = []
        if self.role == self.Role.ADMIN:
            roles.append(settings.DISCORD_ROLES['admin'])
        elif self.role == self.Role.MODERATOR:
            roles.append(settings.DISCORD_ROLES['moderator'])
        elif self.role == self.Role.SUPPORT:
            roles.append(settings.DISCORD_ROLES['support'])
        
        # Все пользователи получают базовую роль USER
        roles.append(settings.DISCORD_ROLES['user'])
        
        return [r for r in roles if r]  # Фильтруем пустые значения
    
    def update_invite_limits(self):
        """Обновляет лимиты инвайтов в зависимости от роли"""
        if self.role in settings.INVITE_LIMITS:
            self.monthly_invites_limit = settings.INVITE_LIMITS[self.role]
            self.save(update_fields=['monthly_invites_limit'])


class BindingCode(models.Model):
    """Временный код для привязки Discord аккаунта к аккаунту на сайте"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='binding_codes', verbose_name=_('Пользователь'))
    code = models.CharField(max_length=10, unique=True, verbose_name=_('Код'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Создан'))
    expires_at = models.DateTimeField(verbose_name=_('Истекает'))
    is_used = models.BooleanField(default=False, verbose_name=_('Использован'))
    
    class Meta:
        verbose_name = _('Код привязки')
        verbose_name_plural = _('Коды привязки')
    
    def __str__(self):
        return f"{self.code} ({self.user.username})"
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at 