"""
ASGI config for zalupaspb project.
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zalupaspb.settings')

# Импортируем потребителей WebSocket здесь, чтобы избежать циклических импортов
from users.consumers import UserStatusConsumer
from keys.consumers import KeyStatusConsumer

# Определяем URL-пути для WebSocket
websocket_urlpatterns = [
    path('ws/users/status/', UserStatusConsumer.as_asgi()),
    path('ws/keys/status/', KeyStatusConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
}) 