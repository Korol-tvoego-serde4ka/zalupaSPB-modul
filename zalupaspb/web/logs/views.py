from rest_framework import generics, permissions
from .models import Log
from .serializers import LogSerializer


class IsAdminOrModerator(permissions.BasePermission):
    """Разрешение для админов и модераторов"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'moderator']


class LogListView(generics.ListAPIView):
    """Список логов с фильтрацией"""
    serializer_class = LogSerializer
    permission_classes = [IsAdminOrModerator]
    
    def get_queryset(self):
        """Получение списка логов с фильтрацией"""
        queryset = Log.objects.all()
        
        # Фильтрация по уровню
        level = self.request.query_params.get('level')
        if level:
            queryset = queryset.filter(level=level)
        
        # Фильтрация по категории
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Фильтрация по пользователю
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Фильтрация по IP адресу
        ip_address = self.request.query_params.get('ip_address')
        if ip_address:
            queryset = queryset.filter(ip_address=ip_address)
        
        # Фильтрация по тексту сообщения
        message = self.request.query_params.get('message')
        if message:
            queryset = queryset.filter(message__icontains=message)
        
        # Фильтрация по временному диапазону
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        return queryset


class LogDetailView(generics.RetrieveAPIView):
    """Детальная информация о логе"""
    queryset = Log.objects.all()
    serializer_class = LogSerializer
    permission_classes = [IsAdminOrModerator] 