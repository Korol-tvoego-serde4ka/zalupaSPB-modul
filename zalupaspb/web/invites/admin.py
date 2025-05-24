from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.utils import timezone
from .models import Invite


@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = ['code', 'status_colored', 'created_by', 'created_at', 
                    'used_by', 'used_at', 'expires_at', 'days_remaining']
    list_filter = ['status', 'created_at', 'used_at']
    search_fields = ['code', 'created_by__username', 'used_by__username', 'used_ip']
    readonly_fields = ['id', 'created_at', 'used_at', 'days_remaining']
    actions = ['revoke_invites', 'extend_invites']
    
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('id', 'code', 'status')
        }),
        (_('Создание'), {
            'fields': ('created_by', 'created_at')
        }),
        (_('Использование'), {
            'fields': ('used_by', 'used_at', 'used_ip')
        }),
        (_('Срок действия'), {
            'fields': ('expires_at', 'days_remaining')
        }),
    )
    
    def status_colored(self, obj):
        """Отображение статуса инвайта с цветом"""
        colors = {
            'active': 'green',
            'used': 'blue',
            'expired': 'red',
            'revoked': 'gray',
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_colored.short_description = _('Статус')
    
    def days_remaining(self, obj):
        """Отображение оставшихся дней действия инвайта"""
        if obj.status != 'active':
            return '-'
        
        if not obj.expires_at:
            return '∞'
        
        delta = obj.expires_at - timezone.now()
        days = delta.days
        hours = delta.seconds // 3600
        
        if days < 0:
            return _('Истёк')
        elif days == 0:
            return _('{}ч').format(hours)
        else:
            return _('{}д {}ч').format(days, hours)
    days_remaining.short_description = _('Осталось')
    
    def revoke_invites(self, request, queryset):
        """Отзыв выбранных инвайтов"""
        count = 0
        for invite in queryset:
            if invite.revoke():
                count += 1
        
        self.message_user(request, _(f'Успешно отозвано {count} инвайтов'))
    revoke_invites.short_description = _('Отозвать выбранные инвайты')
    
    def extend_invites(self, request, queryset):
        """Продление срока действия выбранных инвайтов на 7 дней"""
        count = 0
        for invite in queryset:
            if invite.status == 'active':
                invite.expires_at = timezone.now() + timezone.timedelta(days=7)
                invite.save()
                count += 1
        
        self.message_user(request, _(f'Успешно продлено {count} инвайтов на 7 дней'))
    extend_invites.short_description = _('Продлить на 7 дней')
    
    def save_model(self, request, obj, form, change):
        """Сохранение модели с автоматическим созданием истории"""
        is_new = not obj.pk
        
        # Устанавливаем создателя для новых инвайтов
        if is_new:
            obj.created_by = request.user
        
        super().save_model(request, obj, form, change) 