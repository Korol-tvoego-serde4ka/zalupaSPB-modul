from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import path
from datetime import timedelta
from .models import Log


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'level_colored', 'category_colored', 'short_message', 'user', 'ip_address']
    list_filter = ['level', 'category', 'timestamp', 'user']
    search_fields = ['message', 'user__username', 'ip_address']
    readonly_fields = ['id', 'timestamp', 'level', 'category', 'message', 'user', 'ip_address', 'extra_data']
    actions = ['clear_logs_older_than_7_days', 'clear_logs_older_than_30_days', 'clear_all_logs']
    
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('id', 'timestamp', 'level', 'category')
        }),
        (_('Содержание'), {
            'fields': ('message', 'extra_data')
        }),
        (_('Пользователь'), {
            'fields': ('user', 'ip_address')
        }),
    )
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('clear-logs/7-days/', self.admin_site.admin_view(self.clear_logs_7_days), name='clear_logs_7_days'),
            path('clear-logs/30-days/', self.admin_site.admin_view(self.clear_logs_30_days), name='clear_logs_30_days'),
            path('clear-logs/all/', self.admin_site.admin_view(self.clear_logs_all), name='clear_logs_all'),
        ]
        return custom_urls + urls
    
    def clear_logs_7_days(self, request):
        """Очистка логов старше 7 дней через URL"""
        return self._clear_logs(request, days=7)
    
    def clear_logs_30_days(self, request):
        """Очистка логов старше 30 дней через URL"""
        return self._clear_logs(request, days=30)
    
    def clear_logs_all(self, request):
        """Очистка всех логов через URL"""
        return self._clear_logs(request, days=None)
    
    def _clear_logs(self, request, days=None):
        """Общая функция очистки логов"""
        if not request.user.is_superuser:
            self.message_user(request, "Только администраторы могут очищать логи", level=messages.ERROR)
            return HttpResponseRedirect("../")
        
        if days:
            cutoff_date = timezone.now() - timedelta(days=days)
            count, _ = Log.objects.filter(timestamp__lt=cutoff_date).delete()
            self.message_user(request, f"Удалено {count} логов старше {days} дней", level=messages.SUCCESS)
        else:
            count, _ = Log.objects.all().delete()
            self.message_user(request, f"Удалено {count} логов", level=messages.SUCCESS)
        
        return HttpResponseRedirect("../")
    
    def clear_logs_older_than_7_days(self, modeladmin, request, queryset):
        """Действие для очистки логов старше 7 дней"""
        cutoff_date = timezone.now() - timedelta(days=7)
        count, _ = Log.objects.filter(timestamp__lt=cutoff_date).delete()
        self.message_user(request, f"Удалено {count} логов старше 7 дней", level=messages.SUCCESS)
    clear_logs_older_than_7_days.short_description = "Удалить логи старше 7 дней"
    
    def clear_logs_older_than_30_days(self, modeladmin, request, queryset):
        """Действие для очистки логов старше 30 дней"""
        cutoff_date = timezone.now() - timedelta(days=30)
        count, _ = Log.objects.filter(timestamp__lt=cutoff_date).delete()
        self.message_user(request, f"Удалено {count} логов старше 30 дней", level=messages.SUCCESS)
    clear_logs_older_than_30_days.short_description = "Удалить логи старше 30 дней"
    
    def clear_all_logs(self, modeladmin, request, queryset):
        """Действие для очистки всех логов"""
        if not request.user.is_superuser:
            self.message_user(request, "Только администраторы могут очищать все логи", level=messages.ERROR)
            return
        
        count, _ = Log.objects.all().delete()
        self.message_user(request, f"Удалено {count} логов", level=messages.SUCCESS)
    clear_all_logs.short_description = "Удалить все логи"
    
    def changelist_view(self, request, extra_context=None):
        """Переопределение view для добавления кнопок очистки"""
        extra_context = extra_context or {}
        extra_context['show_clear_buttons'] = True
        return super().changelist_view(request, extra_context=extra_context)
    
    def level_colored(self, obj):
        """Отображение уровня лога с цветовой индикацией"""
        colors = {
            'debug': '#6c757d',  # серый
            'info': '#17a2b8',   # голубой
            'warning': '#ffc107', # желтый
            'error': '#fd7e14',   # оранжевый
            'critical': '#dc3545', # красный
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.level, 'black'),
            obj.get_level_display()
        )
    level_colored.short_description = _('Уровень')
    
    def category_colored(self, obj):
        """Отображение категории лога с цветовой индикацией"""
        colors = {
            'user': '#28a745',      # зеленый
            'key': '#0056b3',        # синий
            'invite': '#6f42c1',     # фиолетовый
            'discord': '#5865F2',    # Discord синий
            'system': '#6c757d',     # серый
            'security': '#dc3545',   # красный
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.category, 'black'),
            obj.get_category_display()
        )
    category_colored.short_description = _('Категория')
    
    def short_message(self, obj):
        """Сокращенное сообщение лога для отображения в списке"""
        max_length = 100
        if len(obj.message) > max_length:
            return obj.message[:max_length] + '...'
        return obj.message
    short_message.short_description = _('Сообщение')
    
    def has_add_permission(self, request):
        """Запрет на создание логов через админку"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Запрет на изменение логов"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Разрешаем удаление логов администраторам"""
        return request.user.is_superuser 