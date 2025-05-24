from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.urls import reverse
from invites.models import Invite
from ..serializers import (
    UserCreateSerializer, UserSerializer, 
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer
)
import logging

logger = logging.getLogger('users')
User = get_user_model()


class RegisterAPIView(APIView):
    """Регистрация нового пользователя через API"""
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


class RegisterView(View):
    """Регистрация нового пользователя через веб-форму"""
    template_name = 'registration/register.html'
    
    def get(self, request):
        """Отображение формы регистрации"""
        return render(request, self.template_name)
    
    def post(self, request):
        """Обработка формы регистрации"""
        try:
            # Получаем данные из формы
            invite_code = request.POST.get('invite_code', '')
            username = request.POST.get('username', '')
            email = request.POST.get('email', '')
            password1 = request.POST.get('password1', '')
            password2 = request.POST.get('password2', '')
            
            # Логируем для отладки
            logger.info(f"Registration attempt: username={username}, email={email}, invite_code={invite_code}")
            
            # Базовая валидация
            errors = {}
            
            # Проверка заполнения обязательных полей
            if not invite_code:
                errors['invite_code'] = ['Код приглашения обязателен']
            if not username:
                errors['username'] = ['Имя пользователя обязательно']
            if not email:
                errors['email'] = ['Email обязателен']
            if not password1:
                errors['password1'] = ['Пароль обязателен']
            if not password2:
                errors['password2'] = ['Подтверждение пароля обязательно']
                
            # Если какие-то поля не заполнены, сразу возвращаем ошибки
            if errors:
                return self.render_with_errors(request, errors, {
                    'username': username,
                    'email': email,
                    'invite_code': invite_code
                })
            
            # Проверка пароля
            if password1 != password2:
                errors['password2'] = ['Пароли не совпадают']
            
            # Минимальная длина пароля
            if len(password1) < 8:
                errors['password1'] = ['Пароль должен содержать не менее 8 символов']
            
            # Проверка инвайт-кода
            invite = None
            try:
                invite = Invite.objects.get(code=invite_code, is_used=False)
            except Invite.DoesNotExist:
                errors['invite_code'] = ['Недействительный или использованный код приглашения']
            
            # Проверка имени пользователя
            if User.objects.filter(username=username).exists():
                errors['username'] = ['Пользователь с таким именем уже существует']
            
            # Проверка email
            if User.objects.filter(email=email).exists():
                errors['email'] = ['Пользователь с таким email уже существует']
            
            # Если есть ошибки, возвращаем форму с ошибками
            if errors:
                return self.render_with_errors(request, errors, {
                    'username': username,
                    'email': email,
                    'invite_code': invite_code
                })
            
            # Создаем пользователя
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                invited_by=invite.created_by if invite else None
            )
            
            # Помечаем инвайт использованным
            if invite:
                invite.is_used = True
                invite.used_by = user
                invite.save()
            
            # Логируем событие
            logger.info(f"New user registered via web form: {user.username}")
            
            # Отправляем успешное сообщение
            messages.success(request, 'Регистрация успешно завершена. Теперь вы можете войти в систему.')
            
            # Перенаправляем на страницу входа
            return redirect(reverse('login'))
            
        except Exception as e:
            # Логируем ошибку
            logger.error(f"Registration error: {str(e)}", exc_info=True)
            # Отправляем конкретное сообщение об ошибке
            messages.error(request, f'Ошибка при регистрации: {str(e)}.')
            return self.render_with_errors(request, {}, {
                'username': request.POST.get('username', ''),
                'email': request.POST.get('email', ''),
                'invite_code': request.POST.get('invite_code', '')
            })
    
    def render_with_errors(self, request, errors, form_data):
        """Вспомогательный метод для рендеринга формы с ошибками"""
        context = {
            'form': {
                'errors': errors,
                'form_data': form_data
            }
        }
        return render(request, self.template_name, context)


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