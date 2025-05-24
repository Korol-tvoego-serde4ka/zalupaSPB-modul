from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Key, KeyHistory
from .serializers import KeySerializer, KeyCreateSerializer, KeyHistorySerializer
from django.utils import timezone
import logging

logger = logging.getLogger('keys')


class IsAdminOrModerator(permissions.BasePermission):
    """Разрешение для админов и модераторов"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'moderator']


class KeyListView(generics.ListAPIView):
    """Список ключей"""
    serializer_class = KeySerializer
    permission_classes = [IsAdminOrModerator]
    
    def get_queryset(self):
        """Получение списка ключей с фильтрацией"""
        queryset = Key.objects.all()
        
        # Фильтрация по статусу
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Фильтрация по типу
        key_type = self.request.query_params.get('type')
        if key_type:
            queryset = queryset.filter(key_type=key_type)
        
        # Фильтрация по создателю
        created_by = self.request.query_params.get('created_by')
        if created_by:
            queryset = queryset.filter(created_by=created_by)
        
        # Фильтрация по активированным пользователям
        activated_by = self.request.query_params.get('activated_by')
        if activated_by:
            queryset = queryset.filter(activated_by=activated_by)
        
        return queryset


class KeyDetailView(generics.RetrieveAPIView):
    """Детальная информация о ключе"""
    queryset = Key.objects.all()
    serializer_class = KeySerializer
    permission_classes = [IsAdminOrModerator]
    
    def get(self, request, *args, **kwargs):
        """Получение информации о ключе с историей"""
        key = self.get_object()
        key.check_expiry()  # Проверяем срок действия
        
        # Сериализуем ключ
        key_data = KeySerializer(key).data
        
        # Получаем историю ключа
        history = key.history.all()
        history_data = KeyHistorySerializer(history, many=True).data
        
        # Объединяем данные
        response_data = {
            'key': key_data,
            'history': history_data
        }
        
        return Response(response_data)


class KeyCreateView(APIView):
    """Создание нового ключа"""
    permission_classes = [IsAdminOrModerator]
    
    def post(self, request, *args, **kwargs):
        """Создание нового ключа"""
        serializer = KeyCreateSerializer(data=request.data)
        
        # Получаем IP пользователя
        ip_address = getattr(request, 'client_ip', request.META.get('REMOTE_ADDR', ''))
        
        # Подготавливаем дополнительную информацию для лога
        extra = {
            'user_id': request.user.id,
            'ip_address': ip_address
        }
        
        if serializer.is_valid():
            # Создаем ключ
            key = Key(
                key_type=serializer.validated_data.get('key_type', Key.KeyType.STANDARD),
                duration_days=serializer.validated_data.get('duration_days', 30),
                created_by=request.user,
                notes=serializer.validated_data.get('notes', '')
            )
            key.save()
            
            logger.info(f"User {request.user.username} created key {key.key}", extra=extra)
            
            return Response(KeySerializer(key).data, status=status.HTTP_201_CREATED)
        
        logger.warning(f"Ошибка при создании ключа пользователем {request.user.username}: {serializer.errors}", extra=extra)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class KeyActivateView(APIView):
    """Активация ключа"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk, *args, **kwargs):
        """Активация ключа пользователем"""
        key = get_object_or_404(Key, pk=pk)
        
        # Получаем IP пользователя
        ip_address = getattr(request, 'client_ip', request.META.get('REMOTE_ADDR', ''))
        
        # Подготавливаем дополнительную информацию для лога
        extra = {
            'user_id': request.user.id,
            'ip_address': ip_address
        }
        
        # Проверяем, активен ли ключ
        if not key.is_active:
            logger.warning(f"Попытка активации неактивного ключа {key.key_code} пользователем {request.user.username}", extra=extra)
            return Response(
                {'error': 'Ключ не активен или уже использован'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Активируем ключ
        if key.activate(request.user):
            logger.info(f"User {request.user.username} activated key {key.key}", extra=extra)
            return Response(KeySerializer(key).data)
        
        logger.error(f"Ошибка при активации ключа {key.key_code} пользователем {request.user.username}", extra=extra)
        return Response(
            {'error': 'Не удалось активировать ключ'},
            status=status.HTTP_400_BAD_REQUEST
        )


class KeyRevokeView(APIView):
    """Отзыв ключа"""
    permission_classes = [IsAdminOrModerator]
    
    def post(self, request, pk, *args, **kwargs):
        """Отзыв ключа"""
        key = get_object_or_404(Key, pk=pk)
        
        # Получаем IP пользователя
        ip_address = getattr(request, 'client_ip', request.META.get('REMOTE_ADDR', ''))
        
        # Подготавливаем дополнительную информацию для лога
        extra = {
            'user_id': request.user.id,
            'ip_address': ip_address
        }
        
        # Проверяем, можно ли отозвать ключ
        if key.status in [Key.KeyStatus.EXPIRED, Key.KeyStatus.REVOKED]:
            logger.warning(f"Попытка отзыва уже отозванного или истекшего ключа {key.key_code} пользователем {request.user.username}", extra=extra)
            return Response(
                {'error': 'Ключ уже отозван или истек'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Отзываем ключ
        if key.revoke():
            logger.info(f"User {request.user.username} revoked key {key.key}", extra=extra)
            return Response(KeySerializer(key).data)
        
        logger.error(f"Ошибка при отзыве ключа {key.key_code} пользователем {request.user.username}", extra=extra)
        return Response(
            {'error': 'Не удалось отозвать ключ'},
            status=status.HTTP_400_BAD_REQUEST
        ) 