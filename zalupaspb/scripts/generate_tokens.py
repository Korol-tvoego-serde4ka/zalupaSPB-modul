#!/usr/bin/env python
"""
Скрипт для генерации JWT токенов для API бота.
Используйте: python generate_tokens.py [username] [password]
"""

import os
import sys
import django
from dotenv import load_dotenv

# Добавляем путь к Django проекту
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'web'))

# Загружаем переменные окружения
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', '.env'))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zalupaspb.settings')
django.setup()

# Импортируем нужные модули
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

User = get_user_model()

def create_bot_user(username, password):
    """Создает пользователя для бота или находит существующего"""
    try:
        user = User.objects.get(username=username)
        print(f"Пользователь {username} уже существует")
        
        # Проверяем пароль, если указан
        if password and not check_password(password, user.password):
            print(f"Неверный пароль для пользователя {username}")
            return None
    except User.DoesNotExist:
        if not password:
            print("Необходимо указать пароль для создания нового пользователя")
            return None
            
        # Создаем нового пользователя
        user = User.objects.create_user(
            username=username,
            password=password,
            is_active=True
        )
        print(f"Создан новый пользователь: {username}")
    
    return user

def generate_tokens(user):
    """Генерирует токены доступа и обновления для пользователя"""
    refresh = RefreshToken.for_user(user)
    
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)
    
    return access_token, refresh_token

def save_tokens_to_env(access_token, refresh_token):
    """Сохраняет токены в .env файл"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', '.env')
    
    with open(env_path, 'r') as file:
        lines = file.readlines()
    
    # Обновляем значения токенов
    new_lines = []
    for line in lines:
        if line.startswith('API_TOKEN='):
            new_lines.append(f'API_TOKEN={access_token}\n')
        elif line.startswith('API_REFRESH_TOKEN='):
            new_lines.append(f'API_REFRESH_TOKEN={refresh_token}\n')
        else:
            new_lines.append(line)
    
    # Если строк с токенами нет, добавляем их
    if not any(line.startswith('API_TOKEN=') for line in new_lines):
        new_lines.append(f'API_TOKEN={access_token}\n')
    if not any(line.startswith('API_REFRESH_TOKEN=') for line in new_lines):
        new_lines.append(f'API_REFRESH_TOKEN={refresh_token}\n')
    
    # Записываем обновленные строки обратно в файл
    with open(env_path, 'w') as file:
        file.writelines(new_lines)
    
    print(f"Токены сохранены в {env_path}")

def main():
    """Основная функция скрипта"""
    if len(sys.argv) < 2:
        print("Использование: python generate_tokens.py [username] [password]")
        print("password необходим только для создания нового пользователя")
        return
    
    username = sys.argv[1]
    password = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Получаем или создаем пользователя
    user = create_bot_user(username, password)
    if not user:
        return
    
    # Генерируем токены
    access_token, refresh_token = generate_tokens(user)
    
    # Сохраняем токены в .env файл
    save_tokens_to_env(access_token, refresh_token)
    
    print("\nТокены успешно сгенерированы:")
    print(f"API_TOKEN={access_token}")
    print(f"API_REFRESH_TOKEN={refresh_token}")
    print("\nТокены также сохранены в .env файл")

if __name__ == "__main__":
    main() 