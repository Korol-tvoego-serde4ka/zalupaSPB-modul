from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from .models import User, BindingCode


class BindingCodeInline(admin.TabularInline):
    model = BindingCode
    extra = 0
    readonly_fields = ['code', 'created_at', 'expires_at', 'is_used']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'get_full_name', 'role_colored', 'discord_username',
                    'is_active', 'is_banned', 'date_joined', 'invited_by_link', 'available_invites']
    list_filter = ['role', 'is_active', 'is_banned', 'date_joined', 'last_login']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'discord_id', 'discord_username']
    readonly_fields = ['id', 'date_joined', 'last_login', 'registered_ip', 'last_login_ip']
    inlines = [BindingCodeInline]
    
    fieldsets = (
        (None, {'fields': ('id', 'username', 'password')}),
        (_('Персональная информация'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Роль и права доступа'), {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        (_('Блокировка'), {'fields': ('is_banned', 'ban_reason')}),
        (_('Discord интеграция'), {'fields': ('discord_id', 'discord_username', 'discord_avatar')}),
        (_('Регистрация'), {'fields': ('invited_by', 'registered_ip', 'date_joined')}),
        (_('Инвайты'), {'fields': ('monthly_invites_limit', 'invites_used_this_month', 'last_invite_reset')}),
        (_('Последний вход'), {'fields': ('last_login', 'last_login_ip')}),
        (_('Дополнительно'), {'fields': ('notes',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )
    
    actions = ['ban_users', 'unban_users', 'generate_binding_code', 'reset_invite_limits']
    
    def role_colored(self, obj):
        """Отображение роли пользователя с цветом"""
        colors = {
            'admin': 'red',
            'moderator': 'orange',
            'support': 'purple',
            'user': 'green',
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.role, 'black'),
            obj.get_role_display()
        )
    role_colored.short_description = _('Роль')
    
    def invited_by_link(self, obj):
        """Ссылка на пригласившего пользователя"""
        if not obj.invited_by:
            return '-'
        
        url = reverse('admin:users_user_change', args=[obj.invited_by.id])
        return format_html('<a href="{}">{}</a>', url, obj.invited_by.username)
    invited_by_link.short_description = _('Приглашен')
    
    def available_invites(self, obj):
        """Отображение доступных инвайтов"""
        if obj.role == 'admin':
            return '∞'
        return obj.get_invites_available()
    available_invites.short_description = _('Доступно инвайтов')
    
    def ban_users(self, request, queryset):
        """Блокировка выбранных пользователей"""
        count = queryset.filter(is_banned=False).update(is_banned=True, ban_reason='Заблокирован администратором')
        self.message_user(request, _(f'Заблокировано {count} пользователей'))
    ban_users.short_description = _('Заблокировать выбранных пользователей')
    
    def unban_users(self, request, queryset):
        """Разблокировка выбранных пользователей"""
        count = queryset.filter(is_banned=True).update(is_banned=False, ban_reason='')
        self.message_user(request, _(f'Разблокировано {count} пользователей'))
    unban_users.short_description = _('Разблокировать выбранных пользователей')
    
    def generate_binding_code(self, request, queryset):
        """Генерация кода привязки Discord для выбранных пользователей"""
        from django.utils import timezone
        import random
        import string
        
        count = 0
        for user in queryset:
            # Генерируем случайный код
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            
            # Создаем запись кода привязки
            BindingCode.objects.create(
                user=user,
                code=code,
                expires_at=timezone.now() + timezone.timedelta(minutes=15)
            )
            count += 1
        
        self.message_user(request, _(f'Сгенерировано {count} кодов привязки. Коды действительны 15 минут.'))
    generate_binding_code.short_description = _('Сгенерировать код привязки Discord')
    
    def reset_invite_limits(self, request, queryset):
        """Сброс лимитов инвайтов для выбранных пользователей"""
        from django.utils import timezone
        
        count = 0
        for user in queryset:
            user.invites_used_this_month = 0
            user.last_invite_reset = timezone.now()
            user.save(update_fields=['invites_used_this_month', 'last_invite_reset'])
            count += 1
        
        self.message_user(request, _(f'Сброшены лимиты инвайтов для {count} пользователей'))
    reset_invite_limits.short_description = _('Сбросить лимиты инвайтов')


@admin.register(BindingCode)
class BindingCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'user', 'created_at', 'expires_at', 'is_used', 'is_expired']
    list_filter = ['is_used', 'created_at']
    search_fields = ['code', 'user__username']
    readonly_fields = ['code', 'user', 'created_at', 'expires_at', 'is_used']
    
    def is_expired(self, obj):
        """Отображение истечения срока кода"""
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = _('Истёк')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False 