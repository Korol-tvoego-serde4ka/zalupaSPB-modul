from rest_framework import serializers
from .models import Invite


class InviteSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Invite"""
    created_by_username = serializers.SerializerMethodField()
    used_by_username = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    remaining_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Invite
        fields = [
            'id', 'code', 'created_by', 'created_by_username', 'created_at',
            'status', 'status_display', 'used_by', 'used_by_username', 'used_at',
            'used_ip', 'expires_at', 'is_active', 'remaining_time'
        ]
    
    def get_created_by_username(self, obj):
        """Получение имени создателя инвайта"""
        return obj.created_by.username
    
    def get_used_by_username(self, obj):
        """Получение имени пользователя, использовавшего инвайт"""
        if obj.used_by:
            return obj.used_by.username
        return None
    
    def get_status_display(self, obj):
        """Получение отображаемого значения статуса инвайта"""
        return obj.get_status_display()
    
    def get_is_active(self, obj):
        """Проверка активности инвайта"""
        return obj.is_active
    
    def get_remaining_time(self, obj):
        """Получение оставшегося времени действия инвайта в часах"""
        from django.utils import timezone
        if not obj.is_active:
            return 0
        
        delta = obj.expires_at - timezone.now()
        seconds = delta.total_seconds()
        return max(0, round(seconds / 3600, 1))  # Округляем до десятых часа


class InviteCreateSerializer(serializers.Serializer):
    """Сериализатор для создания инвайта"""
    expires_days = serializers.IntegerField(required=False, min_value=1, max_value=30, default=7)


class InviteValidateSerializer(serializers.Serializer):
    """Сериализатор для проверки инвайт-кода"""
    code = serializers.CharField(max_length=15)
    
    def validate_code(self, value):
        """Валидация кода инвайта"""
        try:
            invite = Invite.objects.get(code=value)
            if not invite.is_active:
                raise serializers.ValidationError("Инвайт-код не активен или уже использован")
            return value
        except Invite.DoesNotExist:
            raise serializers.ValidationError("Инвайт-код не существует") 