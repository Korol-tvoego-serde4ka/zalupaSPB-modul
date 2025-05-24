import logging
import json
import requests
from django.conf import settings
from .models import Log


class DatabaseLogHandler(logging.Handler):
    """Обработчик логов для сохранения в базу данных"""
    
    def emit(self, record):
        """Сохранение лога в базу данных"""
        try:
            # Форматируем сообщение
            message = self.format(record)
            
            # Определяем категорию по имени логгера
            category = Log.LogCategory.SYSTEM
            if record.name.startswith('users'):
                category = Log.LogCategory.USER
            elif record.name.startswith('keys'):
                category = Log.LogCategory.KEY
            elif record.name.startswith('invites'):
                category = Log.LogCategory.INVITE
            elif record.name.startswith('discord'):
                category = Log.LogCategory.DISCORD
            elif record.name.startswith('security'):
                category = Log.LogCategory.SECURITY
            
            # Определяем уровень лога
            level = Log.LogLevel.INFO
            if record.levelno >= logging.CRITICAL:
                level = Log.LogLevel.CRITICAL
            elif record.levelno >= logging.ERROR:
                level = Log.LogLevel.ERROR
            elif record.levelno >= logging.WARNING:
                level = Log.LogLevel.WARNING
            elif record.levelno <= logging.DEBUG:
                level = Log.LogLevel.DEBUG
            
            # Получаем дополнительные данные из записи лога
            extra_data = {}
            for key, value in record.__dict__.items():
                if key not in ['msg', 'args', 'exc_info', 'exc_text', 'message', 'levelname', 'pathname', 'filename',
                              'module', 'lineno', 'funcName', 'created', 'msecs', 'relativeCreated', 'levelno', 'name']:
                    try:
                        # Пытаемся конвертировать значение в JSON-сериализуемый формат
                        json.dumps({key: value})
                        extra_data[key] = value
                    except (TypeError, OverflowError):
                        # Если не удалось, преобразуем в строку
                        extra_data[key] = str(value)
            
            # Создаем запись в базе данных
            Log.objects.create(
                level=level,
                category=category,
                message=message,
                user_id=getattr(record, 'user_id', None),
                ip_address=getattr(record, 'ip_address', None),
                extra_data=extra_data if extra_data else None
            )
        except Exception as e:
            # В случае ошибки записываем в стандартный журнал
            print(f"Error saving log to database: {e}")


class DiscordWebhookHandler(logging.Handler):
    """Обработчик логов для отправки в Discord через webhook"""
    
    def __init__(self, webhook_url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.webhook_url = webhook_url or getattr(settings, 'DISCORD_WEBHOOK_URL', None)
    
    def emit(self, record):
        """Отправка лога в Discord"""
        if not self.webhook_url:
            return
        
        try:
            # Форматируем сообщение
            message = self.format(record)
            
            # Определяем цвет в зависимости от уровня лога
            color = 0x7289DA  # Blue (default)
            if record.levelno >= logging.CRITICAL:
                color = 0xFF0000  # Red
            elif record.levelno >= logging.ERROR:
                color = 0xFF9900  # Orange
            elif record.levelno >= logging.WARNING:
                color = 0xFFCC00  # Yellow
            elif record.levelno <= logging.DEBUG:
                color = 0x808080  # Gray
            
            # Создаем embed для Discord
            embed = {
                "title": f"[{record.levelname}] {record.name}",
                "description": message,
                "color": color,
                "timestamp": None,  # Discord автоматически добавит текущее время
                "fields": []
            }
            
            # Добавляем информацию о пользователе, если она есть
            user_id = getattr(record, 'user_id', None)
            if user_id:
                embed["fields"].append({
                    "name": "User ID",
                    "value": str(user_id),
                    "inline": True
                })
            
            # Добавляем IP адрес, если он есть
            ip_address = getattr(record, 'ip_address', None)
            if ip_address:
                embed["fields"].append({
                    "name": "IP Address",
                    "value": ip_address,
                    "inline": True
                })
            
            # Отправляем запрос в Discord
            payload = {
                "embeds": [embed]
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
        except Exception as e:
            # В случае ошибки записываем в стандартный журнал
            print(f"Error sending log to Discord: {e}") 