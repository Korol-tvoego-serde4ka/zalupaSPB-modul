from rest_framework import serializers
from .models import Key, KeyHistory


class KeySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Key"""
    created_by_username = serializers.SerializerMethodField()
    activated_by_username = serializers.SerializerMethodField()
    key_type_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    remaining_days = serializers.SerializerMethodField()
    
    class Meta:
        model = Key
        fields = [
            'id', 'key', 'key_type', 'key_type_display', 'status', 'status_display',
            'created_by', 'created_by_username', 'created_at', 
            'activated_by', 'activated_by_username', 'activated_at',
            'duration_days', 'expires_at', 'notes', 'remaining_days'
        ]
    
    def get_created_by_username(self, obj):
        """Получение имени создателя ключа"""
        if obj.created_by:
            return obj.created_by.username
        return None
    
    def get_activated_by_username(self, obj):
        """Получение имени пользователя, активировавшего ключ"""
        if obj.activated_by:
            return obj.activated_by.username
        return None
    
    def get_key_type_display(self, obj):
        """Получение отображаемого значения типа ключа"""
        return obj.get_key_type_display()
    
    def get_status_display(self, obj):
        """Получение отображаемого значения статуса ключа"""
        return obj.get_status_display()
    
    def get_remaining_days(self, obj):
        """Получение оставшегося срока действия ключа"""
        return obj.remaining_days


class KeyCreateSerializer(serializers.Serializer):
    """Сериализатор для создания ключа"""
    key_type = serializers.ChoiceField(choices=Key.KeyType.choices, default=Key.KeyType.STANDARD)
    duration_days = serializers.IntegerField(default=30, min_value=1, max_value=3650)
    notes = serializers.CharField(allow_blank=True, required=False)


class KeyHistorySerializer(serializers.ModelSerializer):
    """Сериализатор для истории ключа"""
    user_username = serializers.SerializerMethodField()
    action_display = serializers.SerializerMethodField()
    
    class Meta:
        model = KeyHistory
        fields = ['id', 'action', 'action_display', 'user', 'user_username', 'timestamp', 'details']
    
    def get_user_username(self, obj):
        """Получение имени пользователя, выполнившего действие"""
        if obj.user:
            return obj.user.username
        return None
    
    def get_action_display(self, obj):
        """Получение отображаемого значения действия"""
        return obj.get_action_display() 