#!/usr/bin/env python
"""
Скрипт для отладки проблем с Django и Gunicorn
"""

import os
import sys
import logging
import django

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('debug_django')

# Добавляем путь к Django проекту
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'web'))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zalupaspb.settings')
os.environ.setdefault('DJANGO_DEBUG', 'True')

try:
    logger.info("Инициализация Django...")
    django.setup()
    
    # Импортируем необходимые модули
    from django.conf import settings
    from django.core.wsgi import get_wsgi_application
    from django.core.asgi import get_asgi_application
    
    # Выводим информацию о настройках
    logger.info(f"DEBUG: {settings.DEBUG}")
    logger.info(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    logger.info(f"INSTALLED_APPS: {settings.INSTALLED_APPS}")
    logger.info(f"MIDDLEWARE: {settings.MIDDLEWARE}")
    logger.info(f"ROOT_URLCONF: {settings.ROOT_URLCONF}")
    logger.info(f"WSGI_APPLICATION: {settings.WSGI_APPLICATION}")
    logger.info(f"ASGI_APPLICATION: {settings.ASGI_APPLICATION}")
    
    # Проверяем работу WSGI и ASGI
    logger.info("Проверка WSGI приложения...")
    wsgi_app = get_wsgi_application()
    logger.info(f"WSGI приложение: {wsgi_app}")
    
    logger.info("Проверка ASGI приложения...")
    asgi_app = get_asgi_application()
    logger.info(f"ASGI приложение: {asgi_app}")
    
    # Проверяем URL конфигурацию
    logger.info("Проверка URL конфигурации...")
    from django.urls import get_resolver
    resolver = get_resolver()
    logger.info(f"URL шаблоны: {resolver.url_patterns}")
    
    logger.info("Django настроен корректно!")
    
except Exception as e:
    logger.error(f"Ошибка инициализации Django: {e}")
    import traceback
    logger.error(traceback.format_exc())
    sys.exit(1)

def main():
    logger.info("Все проверки пройдены успешно!")

if __name__ == "__main__":
    main() 