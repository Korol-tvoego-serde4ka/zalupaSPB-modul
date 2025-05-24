import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import User


class UserStatusConsumer(AsyncWebsocketConsumer):
    """WebSocket потребитель для обновлений статуса пользователей"""
    
    async def connect(self):
        """Обработка подключения к WebSocket"""
        # Проверяем аутентификацию пользователя
        if self.scope["user"].is_anonymous:
            await self.close()
            return
        
        # Получаем роль пользователя
        user_role = await self.get_user_role(self.scope["user"])
        
        # Только админам, модераторам и поддержке разрешено подписываться на обновления статуса пользователей
        if user_role not in ['admin', 'moderator', 'support']:
            await self.close()
            return
        
        # Подключаем пользователя к группе обновлений статуса
        await self.channel_layer.group_add(
            'user_status_updates',
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Обработка отключения от WebSocket"""
        # Отключаем пользователя от группы обновлений статуса
        await self.channel_layer.group_discard(
            'user_status_updates',
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Обработка сообщений от клиента"""
        # В данной реализации клиент не отправляет сообщения серверу
        pass
    
    async def user_status_update(self, event):
        """Отправка обновления статуса пользователя клиенту"""
        await self.send(text_data=json.dumps({
            'type': 'user_status_update',
            'user_id': event['user_id'],
            'status': event['status'],
            'timestamp': event['timestamp'],
        }))
    
    @database_sync_to_async
    def get_user_role(self, user):
        """Получение роли пользователя из базы данных"""
        return user.role 