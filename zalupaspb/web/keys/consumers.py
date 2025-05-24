import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class KeyStatusConsumer(AsyncWebsocketConsumer):
    """WebSocket потребитель для обновлений статуса ключей"""
    
    async def connect(self):
        """Обработка подключения к WebSocket"""
        # Проверяем аутентификацию пользователя
        if self.scope["user"].is_anonymous:
            await self.close()
            return
        
        # Получаем роль пользователя
        user_role = await self.get_user_role(self.scope["user"])
        
        # Только админам и модераторам разрешено подписываться на обновления статуса ключей
        if user_role not in ['admin', 'moderator']:
            await self.close()
            return
        
        # Подключаем пользователя к группе обновлений статуса ключей
        await self.channel_layer.group_add(
            'key_status_updates',
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Обработка отключения от WebSocket"""
        # Отключаем пользователя от группы обновлений статуса
        await self.channel_layer.group_discard(
            'key_status_updates',
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Обработка сообщений от клиента"""
        try:
            data = json.loads(text_data)
            
            # Обрабатываем запрос на получение статуса ключа
            if data.get('action') == 'get_key_status' and data.get('key_id'):
                key_status = await self.get_key_status(data['key_id'])
                
                if key_status:
                    await self.send(text_data=json.dumps({
                        'type': 'key_status_response',
                        'key_id': data['key_id'],
                        'status': key_status['status'],
                        'remaining_days': key_status['remaining_days'],
                        'timestamp': timezone.now().isoformat(),
                    }))
        except json.JSONDecodeError:
            pass
    
    async def key_status_update(self, event):
        """Отправка обновления статуса ключа клиенту"""
        await self.send(text_data=json.dumps({
            'type': 'key_status_update',
            'key_id': event['key_id'],
            'status': event['status'],
            'action': event['action'],
            'timestamp': event['timestamp'],
        }))
    
    @database_sync_to_async
    def get_user_role(self, user):
        """Получение роли пользователя из базы данных"""
        return user.role
    
    @database_sync_to_async
    def get_key_status(self, key_id):
        """Получение статуса ключа из базы данных"""
        from .models import Key
        try:
            key = Key.objects.get(id=key_id)
            key.check_expiry()  # Проверяем и обновляем статус, если срок истек
            return {
                'status': key.status,
                'remaining_days': key.remaining_days,
            }
        except Key.DoesNotExist:
            return None 