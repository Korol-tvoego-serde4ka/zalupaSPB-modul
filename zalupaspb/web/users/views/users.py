from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ..serializers import (
    UserSerializer, UserUpdateSerializer, 
    DiscordBindingCodeSerializer, DiscordBindSerializer
)
from ..models import BindingCode
import logging

logger = logging.getLogger('users')
User = get_user_model()


class IsAdminOrModerator(permissions.BasePermission):
    """Разрешение для админов и модераторов"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'moderator']


class IsAdminOrModeratorOrOwner(permissions.BasePermission):
    """Разрешение для админов, модераторов или владельца аккаунта"""
    
    def has_object_permission(self, request, view, obj):
        # Проверяем, аутентифицирован ли пользователь
        if not request.user.is_authenticated:
            return False
            
        # Админы и модераторы имеют доступ ко всем аккаунтам
        if request.user.role in ['admin', 'moderator']:
            return True
            
        # Пользователь имеет доступ только к своему аккаунту
        return obj == request.user


class UserListView(generics.ListAPIView):
    """Список пользователей"""
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrModerator]
    
    def get_queryset(self):
        """Получение списка пользователей с фильтрацией"""
        queryset = User.objects.all()
        
        # Фильтрация по роли
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        # Фильтрация по статусу бана
        is_banned = self.request.query_params.get('is_banned')
        if is_banned is not None:
            is_banned = is_banned.lower() == 'true'
            queryset = queryset.filter(is_banned=is_banned)
        
        # Фильтрация по имени пользователя
        username = self.request.query_params.get('username')
        if username:
            queryset = queryset.filter(username__icontains=username)
        
        # Фильтрация по Discord ID
        discord_id = self.request.query_params.get('discord_id')
        if discord_id:
            queryset = queryset.filter(discord_id=discord_id)
        
        # Фильтрация по пригласившему пользователю
        invited_by = self.request.query_params.get('invited_by')
        if invited_by:
            queryset = queryset.filter(invited_by=invited_by)
        
        return queryset


class UserDetailView(generics.RetrieveAPIView):
    """Детальная информация о пользователе"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrModeratorOrOwner]


class UserUpdateView(generics.UpdateAPIView):
    """Обновление информации о пользователе"""
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAdminOrModeratorOrOwner]
    
    def update(self, request, *args, **kwargs):
        """Обновление пользователя с проверкой прав"""
        # Только админы могут менять роль пользователя
        if 'role' in request.data and request.user.role != 'admin':
            return Response(
                {'role': ['Только администраторы могут изменять роли пользователей']},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Только админы могут менять лимиты инвайтов
        if 'monthly_invites_limit' in request.data and request.user.role != 'admin':
            return Response(
                {'monthly_invites_limit': ['Только администраторы могут изменять лимиты инвайтов']},
                status=status.HTTP_403_FORBIDDEN
            )
        
        response = super().update(request, *args, **kwargs)
        
        # Логируем изменение пользователя
        user = self.get_object()
        logger.info(f"User {user.username} updated by {request.user.username}")
        
        return response


class UserDeleteView(generics.DestroyAPIView):
    """Удаление пользователя"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrModerator]
    
    def destroy(self, request, *args, **kwargs):
        """Удаление пользователя"""
        user = self.get_object()
        
        # Проверка, что админ не пытается удалить другого админа
        if user.role == 'admin' and request.user.role != 'admin':
            return Response(
                {'detail': 'Только администраторы могут удалять администраторов'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Логируем удаление пользователя
        logger.info(f"User {user.username} deleted by {request.user.username}")
        
        return super().destroy(request, *args, **kwargs)


class UserBanView(APIView):
    """Блокировка пользователя"""
    permission_classes = [IsAdminOrModerator]
    
    def post(self, request, pk, *args, **kwargs):
        """Блокировка пользователя"""
        user = get_object_or_404(User, pk=pk)
        
        # Проверка, что модератор не пытается забанить админа
        if user.role == 'admin' and request.user.role != 'admin':
            return Response(
                {'detail': 'Только администраторы могут блокировать администраторов'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Устанавливаем блокировку
        user.is_banned = True
        user.ban_reason = request.data.get('reason', '')
        user.save()
        
        # Логируем блокировку
        logger.info(f"User {user.username} banned by {request.user.username}. Reason: {user.ban_reason}")
        
        return Response(UserSerializer(user).data)


class UserUnbanView(APIView):
    """Разблокировка пользователя"""
    permission_classes = [IsAdminOrModerator]
    
    def post(self, request, pk, *args, **kwargs):
        """Разблокировка пользователя"""
        user = get_object_or_404(User, pk=pk)
        
        # Снимаем блокировку
        user.is_banned = False
        user.ban_reason = None
        user.save()
        
        # Логируем разблокировку
        logger.info(f"User {user.username} unbanned by {request.user.username}")
        
        return Response(UserSerializer(user).data)


class UserRoleUpdateView(APIView):
    """Изменение роли пользователя"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk, *args, **kwargs):
        """Изменение роли пользователя"""
        # Только админы могут менять роли
        if request.user.role != 'admin':
            return Response(
                {'detail': 'Только администраторы могут изменять роли пользователей'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = get_object_or_404(User, pk=pk)
        role = request.data.get('role')
        
        # Проверка валидности роли
        if role not in dict(User.Role.choices).keys():
            return Response(
                {'role': ['Недопустимое значение роли']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Устанавливаем новую роль
        old_role = user.role
        user.role = role
        user.save()
        
        # Логируем изменение роли
        logger.info(f"User {user.username} role changed from {old_role} to {role} by {request.user.username}")
        
        return Response(UserSerializer(user).data)


class DiscordBindingCodeView(APIView):
    """Создание кода для привязки Discord аккаунта"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """Создание нового кода привязки"""
        # Проверяем, есть ли уже активный код
        active_codes = BindingCode.objects.filter(
            user=request.user,
            is_used=False,
            expires_at__gt=timezone.now()
        )
        
        # Если есть активный код, возвращаем его
        if active_codes.exists():
            serializer = DiscordBindingCodeSerializer(active_codes.first())
            return Response(serializer.data)
        
        # Создаем новый код
        serializer = DiscordBindingCodeSerializer(
            data={},
            context={'request': request}
        )
        
        if serializer.is_valid():
            binding_code = serializer.save()
            logger.info(f"Discord binding code created for user {request.user.username}: {binding_code.code}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DiscordBindView(APIView):
    """Привязка Discord аккаунта к пользователю"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        """Привязка Discord аккаунта"""
        serializer = DiscordBindSerializer(data=request.data)
        
        if serializer.is_valid():
            code = serializer.validated_data['code']
            discord_id = serializer.validated_data['discord_id']
            discord_username = serializer.validated_data['discord_username']
            discord_avatar = serializer.validated_data.get('discord_avatar', '')
            
            # Получаем код привязки
            binding_code = BindingCode.objects.get(code=code, is_used=False)
            
            # Привязываем Discord аккаунт к пользователю
            user = binding_code.user
            user.discord_id = discord_id
            user.discord_username = discord_username
            user.discord_avatar = discord_avatar
            user.save()
            
            # Отмечаем код как использованный
            binding_code.is_used = True
            binding_code.save()
            
            logger.info(f"Discord account {discord_username} ({discord_id}) linked to user {user.username}")
            
            return Response({
                'message': 'Discord аккаунт успешно привязан',
                'user': UserSerializer(user).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 