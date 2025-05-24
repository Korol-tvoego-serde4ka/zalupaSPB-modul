from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
import uuid
import string
import random


class Invite(models.Model):
    """Модель инвайт-кода для регистрации новых пользователей"""
    
    class InviteStatus(models.TextChoices):
        ACTIVE = 'active', _('Активный')
        USED = 'used', _('Использован')
        EXPIRED = 'expired', _('Истёк')
        REVOKED = 'revoked', _('Отозван')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=12, unique=True, verbose_name=_('Код инвайта'))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_invites',
        verbose_name=_('Создан пользователем')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    
    status = models.CharField(
        max_length=20,
        choices=InviteStatus.choices,
        default=InviteStatus.ACTIVE,
        verbose_name=_('Статус')
    )
    
    # Информация об использовании
    used_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='used_invite',
        verbose_name=_('Использован пользователем')
    )
    used_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Дата использования'))
    
    # IP адрес, с которого был использован инвайт
    used_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name=_('IP при использовании'))
    
    # Срок действия инвайта (по умолчанию 7 дней)
    expires_at = models.DateTimeField(verbose_name=_('Истекает'))
    
    class Meta:
        verbose_name = _('Инвайт')
        verbose_name_plural = _('Инвайты')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} ({self.created_by.username})"
    
    def save(self, *args, **kwargs):
        # Генерируем код инвайта, если он еще не создан
        if not self.code:
            self.code = self.generate_code()
        
        # Устанавливаем срок действия, если он не задан
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=7)
        
        super().save(*args, **kwargs)
    
    def use(self, user, ip_address=None):
        """Использование инвайта пользователем"""
        if self.status != self.InviteStatus.ACTIVE:
            return False
        
        self.used_by = user
        self.used_at = timezone.now()
        self.used_ip = ip_address
        self.status = self.InviteStatus.USED
        self.save()
        
        # Увеличиваем счетчик использованных инвайтов у создателя
        creator = self.created_by
        creator.invites_used_this_month += 1
        creator.save(update_fields=['invites_used_this_month'])
        
        return True
    
    def revoke(self):
        """Отзыв инвайта"""
        if self.status not in [self.InviteStatus.ACTIVE]:
            return False
        
        self.status = self.InviteStatus.REVOKED
        self.save()
        return True
    
    def check_expiry(self):
        """Проверка истечения срока инвайта"""
        if self.status == self.InviteStatus.ACTIVE:
            if timezone.now() > self.expires_at:
                self.status = self.InviteStatus.EXPIRED
                self.save()
        return self.status
    
    @property
    def is_active(self):
        """Проверка активности инвайта"""
        self.check_expiry()
        return self.status == self.InviteStatus.ACTIVE
    
    @classmethod
    def generate_code(cls):
        """Генерация уникального кода инвайта"""
        chars = string.ascii_uppercase + string.digits
        while True:
            # Генерируем код формата XXXX-XXXX-XXXX
            code = ''.join(random.choices(chars, k=4)) + '-' + \
                   ''.join(random.choices(chars, k=4)) + '-' + \
                   ''.join(random.choices(chars, k=4))
            
            if not cls.objects.filter(code=code).exists():
                return code 