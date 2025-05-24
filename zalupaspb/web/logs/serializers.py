from rest_framework import serializers
from .models import Log


class LogSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Log"""
    level_display = serializers.SerializerMethodField()
    category_display = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    
    class Meta:
        model = Log
        fields = [
            'id', 'timestamp', 'level', 'level_display', 'category', 
            'category_display', 'message', 'user', 'username', 
            'ip_address', 'extra_data'
        ]
    
    def get_level_display(self, obj):
        """Получение отображаемого значения уровня лога"""
        return obj.get_level_display()
    
    def get_category_display(self, obj):
        """Получение отображаемого значения категории лога"""
        return obj.get_category_display()
    
    def get_username(self, obj):
        """Получение имени пользователя"""
        if obj.user:
            return obj.user.username
        return None 