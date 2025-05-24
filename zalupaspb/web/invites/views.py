from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Invite
from .serializers import InviteSerializer, InviteCreateSerializer, InviteValidateSerializer
import logging

logger = logging.getLogger('invites')


class InviteListView(generics.ListAPIView):
    """Список инвайтов текущего пользователя"""
    serializer_class = InviteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Получение списка инвайтов с фильтрацией"""
        # Для админов и модераторов показываем все инвайты
        if self.request.user.role in ['admin', 'moderator']:
            queryset = Invite.objects.all()
        else:
            # Для обычных пользователей только их инвайты
            queryset = Invite.objects.filter(created_by=self.request.user)
        
        # Фильтрация по статусу
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset


class InviteCreateView(APIView):
    """Создание нового инвайта и получение списка инвайтов"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """Получение списка инвайтов (перенаправляем на функционал InviteListView)"""
        # Для админов и модераторов показываем все инвайты
        if request.user.role in ['admin', 'moderator']:
            queryset = Invite.objects.all()
        else:
            # Для обычных пользователей только их инвайты
            queryset = Invite.objects.filter(created_by=request.user)
        
        # Фильтрация по статусу
        status_param = request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        serializer = InviteSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request, *args, **kwargs):
        """Создание нового инвайта"""
        serializer = InviteCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            # Проверяем, есть ли у пользователя доступные инвайты
            available_invites = request.user.get_invites_available()
            
            # Только админам разрешено превышать лимит инвайтов
            if available_invites <= 0 and request.user.role != 'admin':
                return Response(
                    {'error': 'У вас нет доступных инвайтов'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Создаем инвайт
            expires_days = serializer.validated_data.get('expires_days', 7)
            expires_at = timezone.now() + timezone.timedelta(days=expires_days)
            
            invite = Invite(
                created_by=request.user,
                expires_at=expires_at
            )
            invite.save()
            
            # Увеличиваем счетчик использованных инвайтов для всех, кроме админов
            if request.user.role != 'admin':
                request.user.invites_used_this_month += 1
                request.user.save(update_fields=['invites_used_this_month'])
            
            logger.info(f"User {request.user.username} created invite {invite.code}")
            
            return Response(InviteSerializer(invite).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InviteDetailView(generics.RetrieveAPIView):
    """Детальная информация об инвайте"""
    serializer_class = InviteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Для админов и модераторов показываем все инвайты
        if self.request.user.role in ['admin', 'moderator']:
            return Invite.objects.all()
        # Для обычных пользователей только их инвайты
        return Invite.objects.filter(created_by=self.request.user)


class InviteRevokeView(APIView):
    """Отзыв инвайта"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk, *args, **kwargs):
        """Отзыв инвайта"""
        # Находим инвайт
        if request.user.role in ['admin', 'moderator']:
            invite = get_object_or_404(Invite, pk=pk)
        else:
            invite = get_object_or_404(Invite, pk=pk, created_by=request.user)
        
        # Проверяем, можно ли отозвать инвайт
        if invite.status != Invite.InviteStatus.ACTIVE:
            return Response(
                {'error': 'Инвайт уже использован, истек или отозван'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Отзываем инвайт
        if invite.revoke():
            logger.info(f"User {request.user.username} revoked invite {invite.code}")
            return Response(InviteSerializer(invite).data)
        
        return Response(
            {'error': 'Не удалось отозвать инвайт'},
            status=status.HTTP_400_BAD_REQUEST
        )


class InviteValidateView(APIView):
    """Проверка валидности инвайт-кода"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        """Проверка валидности инвайт-кода"""
        serializer = InviteValidateSerializer(data=request.data)
        
        if serializer.is_valid():
            code = serializer.validated_data['code']
            try:
                invite = Invite.objects.get(code=code)
                if invite.is_active:
                    return Response({'valid': True, 'created_by': invite.created_by.username})
                else:
                    return Response({'valid': False, 'error': 'Инвайт-код не активен или уже использован'})
            except Invite.DoesNotExist:
                return Response({'valid': False, 'error': 'Инвайт-код не существует'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 