from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Key, KeyHistory, Loader


class KeyHistoryInline(admin.TabularInline):
    model = KeyHistory
    extra = 0
    readonly_fields = ['action', 'user', 'timestamp', 'details']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Key)
class KeyAdmin(admin.ModelAdmin):
    list_display = ('key_code', 'key_type', 'status', 'created_at', 'expires_at', 'activated_by')
    list_filter = ('key_type', 'status', 'created_at')
    search_fields = ('key_code', 'key', 'activated_by__username', 'created_by__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('key', 'key_code', 'id', 'created_at', 'activated_at')
    actions = ['revoke_keys']
    inlines = [KeyHistoryInline]
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('id', 'key', 'key_code', 'key_type', 'status', 'notes')
        }),
        (_('Создание и активация'), {
            'fields': ('created_by', 'created_at', 'activated_by', 'activated_at')
        }),
        (_('Срок действия'), {
            'fields': ('duration_days', 'expires_at')
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        """Динамически определяем readonly_fields для избежания проблем с property-полями"""
        return self.readonly_fields
    
    def revoke_keys(self, request, queryset):
        updated = 0
        for key in queryset:
            if key.status == 'active' or key.status == 'used':
                key.revoke()
                updated += 1
        self.message_user(request, f'Отозвано {updated} ключей.')
    revoke_keys.short_description = "Отозвать выбранные ключи"


@admin.register(KeyHistory)
class KeyHistoryAdmin(admin.ModelAdmin):
    list_display = ('key_display', 'action', 'user', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('key__key_code', 'key__key', 'user__username')
    date_hierarchy = 'timestamp'
    readonly_fields = ('key', 'action', 'user', 'timestamp', 'details')
    
    def key_display(self, obj):
        """Отображение кода ключа вместо внутреннего ID"""
        if obj.key and obj.key.key_code:
            return obj.key.key_code
        return str(obj.key)
    key_display.short_description = _('Ключ')


@admin.register(Loader)
class LoaderAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'version_type', 'upload_date', 'uploaded_by', 'is_active', 'download_count')
    list_filter = ('version_type', 'is_active', 'upload_date')
    search_fields = ('name', 'version', 'description')
    date_hierarchy = 'upload_date'
    readonly_fields = ('upload_date', 'uploaded_by', 'download_count')
    actions = ['make_active', 'make_inactive']
    
    def save_model(self, request, obj, form, change):
        if not change:  # Если это новая запись
            obj.uploaded_by = request.user
        obj.save()
    
    def make_active(self, request, queryset):
        # При активации одного лоадера, деактивируем все остальные
        Loader.objects.all().update(is_active=False)
        updated = queryset.update(is_active=True)
        self.message_user(request, f'Активирован {updated} лоадер. Все остальные деактивированы.')
    make_active.short_description = "Сделать активным (деактивирует все остальные)"
    
    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'Деактивировано {updated} лоадеров.')
    make_inactive.short_description = "Деактивировать выбранные лоадеры" 