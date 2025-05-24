from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Log


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'level_colored', 'category_colored', 'short_message', 'user', 'ip_address']
    list_filter = ['level', 'category', 'timestamp', 'user']
    search_fields = ['message', 'user__username', 'ip_address']
    readonly_fields = ['id', 'timestamp', 'level', 'category', 'message', 'user', 'ip_address', 'extra_data']
    
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