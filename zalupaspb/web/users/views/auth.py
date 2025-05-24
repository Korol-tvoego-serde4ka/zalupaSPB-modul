from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from ..serializers import (
    UserCreateSerializer, UserSerializer, 
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer
)
import logging

logger = logging.getLogger('users')
User = get_user_model()


class RegisterView(APIView):
    """Регистрация нового пользователя"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        """Создание нового пользователя через инвайт"""
        serializer = UserCreateSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"New user registered: {user.username} (invited by {user.invited_by.username})")
            
            return Response(
                UserSerializer(user).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(APIView):
    """Запрос на сброс пароля"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        """Создание токена для сброса пароля"""
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
                
                # Генерация токена
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # В реальном приложении здесь будет отправка email
                # Для целей демонстрации просто возвращаем токен и uid
                
                logger.info(f"Password reset requested for user: {user.username}")
                
                return Response({
                    'message': 'Инструкции по сбросу пароля отправлены на email',
                    'token': token,
                    'uid': uid
                })
                
            except User.DoesNotExist:
                # Не сообщаем о несуществующем пользователе для безопасности
                pass
            
            return Response({
                'message': 'Инструкции по сбросу пароля отправлены на email, если аккаунт существует'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """Подтверждение сброса пароля"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        """Установка нового пароля по токену"""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if serializer.is_valid():
            # Получаем данные из запроса
            token = serializer.validated_data['token']
            password = serializer.validated_data['password']
            uid = request.data.get('uid')
            
            if not uid:
                return Response(
                    {'uid': ['Это поле обязательно для заполнения']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                # Декодируем uid и получаем пользователя
                user_id = urlsafe_base64_decode(uid).decode()
                user = User.objects.get(pk=user_id)
                
                # Проверяем токен
                if not default_token_generator.check_token(user, token):
                    return Response(
                        {'token': ['Недействительный токен']},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Устанавливаем новый пароль
                user.set_password(password)
                user.save()
                
                logger.info(f"Password reset completed for user: {user.username}")
                
                return Response({'message': 'Пароль успешно изменен'})
                
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return Response(
                    {'uid': ['Недействительный uid']},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 