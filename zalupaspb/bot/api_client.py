import os
import requests
import logging
import json
from dotenv import load_dotenv

# Настройка логирования
logger = logging.getLogger('api_client')

# Загружаем переменные окружения
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', '.env'))

# Настройки API
API_URL = os.getenv('API_URL', 'http://localhost:8000/api')
API_TOKEN = os.getenv('API_TOKEN')


class APIClient:
    """Клиент для работы с API"""
    
    def __init__(self, base_url=None, token=None):
        self.base_url = base_url or API_URL
        self.token = token or API_TOKEN
        self.session = requests.Session()
        
        if self.token:
            self.session.headers.update({'Authorization': f'Bearer {self.token}'})
    
    def _handle_response(self, response):
        """Обработка ответа от API"""
        try:
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
    
    def get_user_by_discord_id(self, discord_id):
        """Получение пользователя по Discord ID"""
        url = f"{self.base_url}/users/?discord_id={discord_id}"
        response = self.session.get(url)
        data = self._handle_response(response)
        
        if 'error' in data:
            return None
        
        if isinstance(data, list) and len(data) > 0:
            return data[0]
        
        return None
    
    def bind_discord(self, code, discord_id, discord_username, discord_avatar=None):
        """Привязка Discord аккаунта к аккаунту пользователя"""
        url = f"{self.base_url}/users/binding/discord/"
        payload = {
            'code': code,
            'discord_id': discord_id,
            'discord_username': discord_username
        }
        
        if discord_avatar:
            payload['discord_avatar'] = discord_avatar
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response)
    
    def create_key(self, key_type='standard', duration_days=30, notes=None):
        """Создание нового ключа"""
        url = f"{self.base_url}/keys/create/"
        payload = {
            'key_type': key_type,
            'duration_days': duration_days
        }
        
        if notes:
            payload['notes'] = notes
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response)
    
    def activate_key(self, key, user_id):
        """Активация ключа"""
        url = f"{self.base_url}/keys/{key}/activate/"
        payload = {
            'user_id': user_id
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response)
    
    def ban_user(self, user_id, reason=None):
        """Блокировка пользователя"""
        url = f"{self.base_url}/users/{user_id}/ban/"
        payload = {}
        
        if reason:
            payload['reason'] = reason
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response)
    
    def unban_user(self, user_id):
        """Разблокировка пользователя"""
        url = f"{self.base_url}/users/{user_id}/unban/"
        response = self.session.post(url, json={})
        return self._handle_response(response)
    
    def get_user_stats(self, user_id):
        """Получение статистики пользователя"""
        url = f"{self.base_url}/users/{user_id}/"
        response = self.session.get(url)
        return self._handle_response(response)
    
    def set_user_role(self, user_id, role):
        """Установка роли пользователя"""
        url = f"{self.base_url}/users/{user_id}/role/"
        payload = {
            'role': role
        }
        
        response = self.session.post(url, json=payload)
        return self._handle_response(response)