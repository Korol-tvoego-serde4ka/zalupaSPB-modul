from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

# Регистрируем модель LogEntry в админке
@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ['action_time', 'user', 'content_type', 'object_repr', 'action_flag', 'change_message']
    list_filter = ['action_time', 'user', 'content_type']
    search_fields = ['object_repr', 'change_message']
    readonly_fields = ['action_time', 'user', 'content_type', 'object_id', 'object_repr', 'action_flag', 'change_message']
    date_hierarchy = 'action_time'
    actions = ['clear_admin_logs']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def clear_admin_logs(self, request, queryset):
        """Очистка всех админ-логов"""
        if not request.user.is_superuser:
            self.message_user(request, "Только администраторы могут очищать логи", level=messages.ERROR)
            return
        
        count, _ = LogEntry.objects.all().delete()
        self.message_user(request, f"Удалено {count} записей действий администраторов", level=messages.SUCCESS)
    clear_admin_logs.short_description = "Удалить все записи действий" 