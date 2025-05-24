from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.shortcuts import render, redirect
from django.urls import path
from django import forms
from .models import Key, KeyHistory, Loader


class KeyHistoryInline(admin.TabularInline):
    model = KeyHistory
    extra = 0
    readonly_fields = ['action', 'user', 'timestamp', 'details']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


class BulkKeyCreationForm(forms.Form):
    """Форма для массового создания ключей"""
    key_codes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 10, 'cols': 40}),
        help_text='Введите ключи по одному на строку. Пустые строки будут пропущены.'
    )
    key_type = forms.ChoiceField(
        choices=Key.KeyType.choices,
        initial=Key.KeyType.STANDARD
    )
    duration_days = forms.IntegerField(
        initial=30,
        min_value=1,
        max_value=3650
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'cols': 40}),
        required=False
    )


@admin.register(Key)
class KeyAdmin(admin.ModelAdmin):
    list_display = ('key_code', 'key_type', 'status', 'created_at', 'expires_at', 'activated_by')
    list_filter = ('key_type', 'status', 'created_at')
    search_fields = ('key_code', 'key', 'activated_by__username', 'created_by__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('key', 'id', 'created_at', 'activated_at')
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

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-create/', self.admin_site.admin_view(self.bulk_create_keys), name='bulk_create_keys'),
        ]
        return custom_urls + urls
    
    def bulk_create_keys(self, request):
        """Массовое создание ключей"""
        if request.method == 'POST':
            form = BulkKeyCreationForm(request.POST)
            if form.is_valid():
                key_codes = form.cleaned_data['key_codes'].strip().split('\n')
                key_type = form.cleaned_data['key_type']
                duration_days = form.cleaned_data['duration_days']
                notes = form.cleaned_data['notes']
                
                created_count = 0
                errors = []
                
                for key_code in key_codes:
                    key_code = key_code.strip()
                    if not key_code:
                        continue
                    
                    # Проверяем, не существует ли уже такой ключ
                    if Key.objects.filter(key_code=key_code).exists():
                        errors.append(f"Ключ '{key_code}' уже существует.")
                        continue
                    
                    try:
                        Key.objects.create(
                            key_code=key_code,
                            key_type=key_type,
                            duration_days=duration_days,
                            notes=notes,
                            created_by=request.user
                        )
                        created_count += 1
                    except Exception as e:
                        errors.append(f"Ошибка при создании ключа '{key_code}': {str(e)}")
                
                if created_count > 0:
                    self.message_user(request, f"Успешно создано {created_count} ключей.")
                
                if errors:
                    for error in errors:
                        self.message_user(request, error, level='error')
                
                return redirect('..')
        else:
            form = BulkKeyCreationForm()
        
        context = {
            'title': 'Массовое создание ключей',
            'form': form,
            'opts': self.model._meta,
        }
        return render(request, 'admin/keys/bulk_create_keys.html', context)

    def get_readonly_fields(self, request, obj=None):
        """Динамически определяем readonly_fields для избежания проблем с property-полями"""
        if obj:  # Если редактируем существующий объект
            return self.readonly_fields
        else:  # Если создаем новый объект, key_code можно редактировать
            return ('key', 'id', 'created_at', 'activated_at')
    
    def revoke_keys(self, request, queryset):
        updated = 0
        for key in queryset:
            if key.status == 'active' or key.status == 'used':
                key.revoke()
                updated += 1
        self.message_user(request, f'Отозвано {updated} ключей.')
    revoke_keys.short_description = "Отозвать выбранные ключи"
    
    def get_changelist_form(self, request, **kwargs):
        """Позволяет редактировать key_code при создании нового ключа"""
        form = super().get_changelist_form(request, **kwargs)
        form.base_fields['key_code'].required = False
        return form
    
    def save_model(self, request, obj, form, change):
        """Устанавливаем создателя ключа при сохранении"""
        if not change:  # Если это новый ключ
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['bulk_create_url'] = './{}/bulk-create/'.format(self.admin_site.name)
        return super().changelist_view(request, extra_context=extra_context)


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