from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger('users')
User = get_user_model()

class IPTrackingModelBackend(ModelBackend):
    """
    Authentication backend, который обновляет IP-адрес при успешном входе пользователя
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('username', '')
        
        if username == '' or password is None:
            return None
        
        # Вызываем стандартную аутентификацию
        user = super().authenticate(request, username=username, password=password, **kwargs)
        
        # Если пользователь успешно аутентифицирован и запрос есть
        if user is not None and request is not None:
            # Получаем IP-адрес из request (установленный нашим middleware)
            ip_address = getattr(request, 'client_ip', request.META.get('REMOTE_ADDR', ''))
            
            # Обновляем IP адрес последнего входа
            if ip_address:
                user.last_login_ip = ip_address
                user.save(update_fields=['last_login_ip'])
                logger.info(f"User {user.username} logged in from IP: {ip_address}")
        
        return user 