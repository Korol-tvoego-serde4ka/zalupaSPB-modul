from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
import random
import string
from .models import BindingCode

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User"""
    role_display = serializers.SerializerMethodField()
    available_invites = serializers.SerializerMethodField()
    invited_by_username = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'role_display', 'discord_id', 'discord_username',
            'discord_avatar', 'is_banned', 'ban_reason', 'date_joined',
            'last_login', 'monthly_invites_limit', 'invites_used_this_month',
            'available_invites', 'invited_by', 'invited_by_username'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'invited_by']
    
    def get_role_display(self, obj):
        """Получение отображаемого значения роли"""
        return obj.get_role_display()
    
    def get_available_invites(self, obj):
        """Получение количества доступных инвайтов"""
        return obj.get_invites_available()
    
    def get_invited_by_username(self, obj):
        """Получение имени пригласившего пользователя"""
        if obj.invited_by:
            return obj.invited_by.username
        return None


class UserUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления пользователя"""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'role',
            'monthly_invites_limit', 'notes'
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователя"""
    invite_code = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'invite_code'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def validate(self, data):
        """Валидация данных"""
        # Проверка совпадения паролей
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Пароли не совпадают'})
        
        # Проверка инвайт-кода
        from invites.models import Invite
        try:
            invite = Invite.objects.get(code=data['invite_code'])
            if not invite.is_active:
                raise serializers.ValidationError({'invite_code': 'Инвайт-код не активен или уже использован'})
        except Invite.DoesNotExist:
            raise serializers.ValidationError({'invite_code': 'Инвайт-код не существует'})
        
        return data
    
    def create(self, validated_data):
        """Создание пользователя"""
        # Получаем инвайт
        from invites.models import Invite
        invite = Invite.objects.get(code=validated_data.pop('invite_code'))
        
        # Удаляем подтверждение пароля из данных
        validated_data.pop('password_confirm')
        
        # Получаем пароль и IP
        password = validated_data.pop('password')
        ip_address = self.context['request'].META.get('REMOTE_ADDR')
        
        # Создаем пользователя
        user = User.objects.create(
            invited_by=invite.created_by,
            registered_ip=ip_address,
            **validated_data
        )
        
        # Устанавливаем пароль
        user.set_password(password)
        user.save()
        
        # Использование инвайта
        invite.use(user, ip_address)
        
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    """Сериализатор для запроса сброса пароля"""
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Сериализатор для подтверждения сброса пароля"""
    token = serializers.CharField()
    password = serializers.CharField(min_length=8, write_only=True)
    password_confirm = serializers.CharField(min_length=8, write_only=True)
    
    def validate(self, data):
        """Валидация данных"""
        # Проверка совпадения паролей
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Пароли не совпадают'})
        return data


class DiscordBindingCodeSerializer(serializers.ModelSerializer):
    """Сериализатор для кода привязки Discord"""
    
    class Meta:
        model = BindingCode
        fields = ['code', 'created_at', 'expires_at', 'is_used']
        read_only_fields = ['code', 'created_at', 'expires_at', 'is_used']
    
    def create(self, validated_data):
        """Создание кода привязки"""
        user = self.context['request'].user
        
        # Генерация случайного кода
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # Установка срока действия кода (15 минут)
        expires_at = timezone.now() + timezone.timedelta(minutes=15)
        
        # Создание и возврат кода привязки
        return BindingCode.objects.create(
            user=user,
            code=code,
            expires_at=expires_at
        )


class DiscordBindSerializer(serializers.Serializer):
    """Сериализатор для привязки Discord аккаунта"""
    code = serializers.CharField()
    discord_id = serializers.CharField()
    discord_username = serializers.CharField()
    discord_avatar = serializers.URLField(required=False, allow_blank=True)
    
    def validate_code(self, value):
        """Валидация кода привязки"""
        try:
            binding_code = BindingCode.objects.get(code=value, is_used=False)
            if binding_code.is_expired:
                raise serializers.ValidationError('Код привязки истек')
            return value
        except BindingCode.DoesNotExist:
            raise serializers.ValidationError('Код привязки не существует или уже использован')
    
    def validate_discord_id(self, value):
        """Валидация Discord ID"""
        # Проверяем, не привязан ли уже этот Discord ID к другому аккаунту
        if User.objects.filter(discord_id=value).exists():
            raise serializers.ValidationError('Этот Discord аккаунт уже привязан к другому пользователю')
        return value 