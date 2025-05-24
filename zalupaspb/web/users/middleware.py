from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger('users')

class IPMiddleware(MiddlewareMixin):
    """Middleware для получения реального IP-адреса пользователя"""
    
    def process_request(self, request):
        """
        Получение IP-адреса из запроса.
        Проверяет различные заголовки, которые могут содержать реальный IP клиента,
        особенно при использовании прокси или балансировщиков.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Получаем первый IP-адрес в цепочке прокси
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            # Или используем REMOTE_ADDR, если X-Forwarded-For отсутствует
            ip = request.META.get('REMOTE_ADDR', '')
            
        # Если это локальный адрес или тестовый сервер, используем фиктивный IP для тестов
        if ip in ['127.0.0.1', 'localhost', '', '::1'] or not ip:
            ip = '192.168.1.1'  # Фиктивный IP для тестирования
        
        # Сохраняем IP в request для использования в других частях приложения
        request.client_ip = ip
        
        # Логируем для отладки
        logger.debug(f"Client IP: {ip}")
        
        return None 