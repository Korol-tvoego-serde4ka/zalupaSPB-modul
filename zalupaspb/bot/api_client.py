import os
import requests
import logging
import json
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Настройка логирования
logger = logging.getLogger('api_client')

# Загружаем переменные окружения
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', '.env'))

# Настройки API
API_URL = os.getenv('API_URL', 'https://dinozavrikgugl.ru/api')
API_TOKEN = os.getenv('API_TOKEN')
API_REFRESH_TOKEN = os.getenv('API_REFRESH_TOKEN')


class APIClient:
    """Клиент для работы с API"""
    
    def __init__(self, base_url=None, token=None, refresh_token=None):
        self.base_url = base_url or API_URL
        self.token = token or API_TOKEN
        self.refresh_token = refresh_token or API_REFRESH_TOKEN
        self.session = requests.Session()
        self.token_expires_at = datetime.now() + timedelta(days=6)  # Предполагаем, что у нас есть 6 дней до истечения токена
        
        if self.token:
            self.update_auth_header()
    
    def update_auth_header(self):
        """Обновляет заголовок авторизации в сессии"""
        self.session.headers.update({'Authorization': f'Bearer {self.token}'})
    
    def refresh_access_token(self):
        """Обновляет access token с помощью refresh token"""
        if not self.refresh_token:
            logger.error("Невозможно обновить токен: refresh_token не указан")
            return False
        
        try:
            url = f"{self.base_url}/token/refresh/"
            response = self.session.post(url, json={'refresh': self.refresh_token})
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access')
                # Если сервер возвращает новый refresh токен
                if 'refresh' in data:
                    self.refresh_token = data.get('refresh')
                    # Сохраняем новые токены в .env файл
                    self._save_tokens_to_env()
                
                self.update_auth_header()
                self.token_expires_at = datetime.now() + timedelta(days=6)  # Устанавливаем новое время истечения
                logger.info("Токен успешно обновлен")
                return True
            else:
                logger.error(f"Ошибка при обновлении токена: {response.status_code} - {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"Исключение при обновлении токена: {e}")
            return False
    
    def _save_tokens_to_env(self):
        """Сохраняет токены в .env файл"""
        try:
            env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', '.env')
            with open(env_path, 'r') as file:
                lines = file.readlines()
            
            # Обновляем значения токенов
            new_lines = []
            for line in lines:
                if line.startswith('API_TOKEN='):
                    new_lines.append(f'API_TOKEN={self.token}\n')
                elif line.startswith('API_REFRESH_TOKEN='):
                    new_lines.append(f'API_REFRESH_TOKEN={self.refresh_token}\n')
                else:
                    new_lines.append(line)
            
            # Если строк с токенами нет, добавляем их
            if not any(line.startswith('API_TOKEN=') for line in new_lines):
                new_lines.append(f'API_TOKEN={self.token}\n')
            if not any(line.startswith('API_REFRESH_TOKEN=') for line in new_lines):
                new_lines.append(f'API_REFRESH_TOKEN={self.refresh_token}\n')
            
            # Записываем обновленные строки обратно в файл
            with open(env_path, 'w') as file:
                file.writelines(new_lines)
            
            logger.info("Токены успешно сохранены в .env файл")
        except Exception as e:
            logger.error(f"Ошибка при сохранении токенов в .env файл: {e}")
    
    def _ensure_token_valid(self):
        """Проверяет, не истек ли токен, и при необходимости обновляет его"""
        # Если до истечения токена осталось менее 1 дня, обновляем его
        if datetime.now() + timedelta(days=1) >= self.token_expires_at:
            return self.refresh_access_token()
        return True
    
    def _handle_response(self, response):
        """Обработка ответа от API"""
        try:
            if response.status_code == 401:  # Unauthorized
                # Пробуем обновить токен и повторить запрос
                if self.refresh_access_token():
                    # Повторяем последний запрос с новым токеном
                    new_response = self.session.request(
                        method=response.request.method,
                        url=response.request.url,
                        data=response.request.body,
                        headers={k: v for k, v in response.request.headers.items() if k != 'Authorization'}
                    )
                    return self._handle_response(new_response)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error: {e}")
            try:
                error_data = response.json()
                logger.error(f"API Error Details: {error_data}")
                return error_data
            except json.JSONDecodeError:
                logger.error(f"Response Text: {response.text}")
                return {'error': str(e)}
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON: {response.text}")
            return {'error': 'Invalid JSON response'}
        except Exception as e:
            logger.error(f"Request Error: {e}")
            return {'error': str(e)}
    
    def _make_request(self, method, endpoint, json_data=None, params=None):
        """Выполняет запрос к API с проверкой валидности токена"""
        if not self._ensure_token_valid():
            return {'error': 'Невозможно обновить токен доступа'}
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=json_data,
                params=params
            )
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Ошибка при выполнении запроса {method} {url}: {e}")
            return {'error': str(e)}

    def get_user_by_discord_id(self, discord_id):
        """Получение пользователя по Discord ID"""
        return self._make_request('GET', '/users/', params={'discord_id': discord_id})
    
    def bind_discord(self, code, discord_id, discord_username, discord_avatar=None):
        """Привязка Discord аккаунта к аккаунту пользователя"""
        payload = {
            'code': code,
            'discord_id': discord_id,
            'discord_username': discord_username
        }
        
        if discord_avatar:
            payload['discord_avatar'] = discord_avatar
        
        return self._make_request('POST', '/users/binding/discord/', json_data=payload)
    
    def create_key(self, key_type='standard', duration_days=30, notes=None):
        """Создание нового ключа"""
        payload = {
            'key_type': key_type,
            'duration_days': duration_days
        }
        
        if notes:
            payload['notes'] = notes
        
        return self._make_request('POST', '/keys/create/', json_data=payload)
    
    def activate_key(self, key, user_id):
        """Активация ключа"""
        payload = {
            'user_id': user_id
        }
        
        return self._make_request('POST', f'/keys/{key}/activate/', json_data=payload)
    
    def ban_user(self, user_id, reason=None):
        """Блокировка пользователя"""
        payload = {}
        
        if reason:
            payload['reason'] = reason
        
        return self._make_request('POST', f'/users/{user_id}/ban/', json_data=payload)
    
    def unban_user(self, user_id):
        """Разблокировка пользователя"""
        return self._make_request('POST', f'/users/{user_id}/unban/', json_data={})
    
    def get_user_stats(self, user_id):
        """Получение статистики пользователя"""
        return self._make_request('GET', f'/users/{user_id}/')
    
    def set_user_role(self, user_id, role):
        """Установка роли пользователя"""
        payload = {
            'role': role
        }
        
        return self._make_request('POST', f'/users/{user_id}/role/', json_data=payload)