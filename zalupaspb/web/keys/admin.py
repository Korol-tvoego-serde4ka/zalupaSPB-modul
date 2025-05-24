from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Key, KeyHistory


class KeyHistoryInline(admin.TabularInline):
    model = KeyHistory
    extra = 0
    readonly_fields = ['action', 'user', 'timestamp', 'details']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Key)
class KeyAdmin(admin.ModelAdmin):
    list_display = ['key', 'key_type', 'status_colored', 'created_by', 'created_at', 
                    'activated_by', 'activated_at', 'expires_at', 'remaining_days']
    list_filter = ['key_type', 'status', 'created_at', 'activated_at']
    search_fields = ['key', 'created_by__username', 'activated_by__username', 'notes']
    readonly_fields = ['id', 'created_at', 'activated_at', 'expires_at', 'remaining_days']
    inlines = [KeyHistoryInline]
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('id', 'key', 'key_type', 'status', 'notes')
        }),
        (_('Создание и активация'), {
            'fields': ('created_by', 'created_at', 'activated_by', 'activated_at')
        }),
        (_('Срок действия'), {
            'fields': ('duration_days', 'expires_at', 'remaining_days')
        }),
    )
    actions = ['activate_keys', 'revoke_keys']

    def status_colored(self, obj):
        """Отображение статуса ключа с цветом"""
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
    
    def activate_keys(self, request, queryset):
        """Активация выбранных ключей"""
        count = 0
        for key in queryset:
            if key.activate(request.user):
                KeyHistory.objects.create(
                    key=key,
                    action=KeyHistory.ActionType.ACTIVATED,
                    user=request.user,
                    details=_('Активирован через административный интерфейс')
                )
                count += 1
        
        self.message_user(request, _(f'Успешно активировано {count} ключей'))
    activate_keys.short_description = _('Активировать выбранные ключи')
    
    def revoke_keys(self, request, queryset):
        """Отзыв выбранных ключей"""
        count = 0
        for key in queryset:
            if key.revoke():
                KeyHistory.objects.create(
                    key=key,
                    action=KeyHistory.ActionType.REVOKED,
                    user=request.user,
                    details=_('Отозван через административный интерфейс')
                )
                count += 1
        
        self.message_user(request, _(f'Успешно отозвано {count} ключей'))
    revoke_keys.short_description = _('Отозвать выбранные ключи')
    
    def save_model(self, request, obj, form, change):
        """Сохранение модели с автоматическим созданием истории"""
        is_new = not obj.pk
        
        # Устанавливаем создателя для новых ключей
        if is_new:
            obj.created_by = request.user
        
        super().save_model(request, obj, form, change)
        
        # Создаем запись в истории
        if is_new:
            KeyHistory.objects.create(
                key=obj,
                action=KeyHistory.ActionType.CREATED,
                user=request.user,
                details=_('Создан через административный интерфейс')
            )


@admin.register(KeyHistory)
class KeyHistoryAdmin(admin.ModelAdmin):
    list_display = ['key', 'action', 'user', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['key__key', 'user__username', 'details']
    readonly_fields = ['key', 'action', 'user', 'timestamp', 'details']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False 