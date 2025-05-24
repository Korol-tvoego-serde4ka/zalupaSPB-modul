# API Reference

ZalupaSPB предоставляет REST API для интеграции с внешними системами и Discord-ботом. Все API-запросы должны использовать JWT-аутентификацию, за исключением публичных эндпоинтов.

## Базовая информация

- **Базовый URL**: `http://your-domain.com/api` или `http://localhost:8000/api` (в режиме разработки)
- **Формат ответа**: JSON
- **Аутентификация**: JWT (Bearer token)

## Аутентификация

### Получение токена

```
POST /api/auth/token/
```

**Параметры запроса:**

```json
{
  "username": "user",
  "password": "password"
}
```

**Ответ:**

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Обновление токена

```
POST /api/auth/token/refresh/
```

**Параметры запроса:**

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Ответ:**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## Пользователи

### Получение списка пользователей

```
GET /api/users/
```

**Параметры запроса:**
- `role` (опционально): Фильтр по роли (admin, moderator, support, user)
- `is_banned` (опционально): Фильтр по статусу бана (true, false)
- `username` (опционально): Поиск по имени пользователя
- `discord_id` (опционально): Фильтр по Discord ID
- `invited_by` (опционально): Фильтр по пригласившему пользователю

**Ответ:**

```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "role_display": "Администратор",
    "discord_id": "123456789012345678",
    "discord_username": "admin#1234",
    "is_banned": false,
    "date_joined": "2023-05-01T12:00:00Z",
    "available_invites": -1
  },
  {
    "id": "223e4567-e89b-12d3-a456-426614174001",
    "username": "user1",
    "email": "user1@example.com",
    "role": "user",
    "role_display": "Пользователь",
    "discord_id": "223456789012345678",
    "discord_username": "user1#5678",
    "is_banned": false,
    "date_joined": "2023-05-02T12:00:00Z",
    "available_invites": 2
  }
]
```

### Получение информации о пользователе

```
GET /api/users/{user_id}/
```

**Ответ:**

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "admin",
  "email": "admin@example.com",
  "first_name": "Admin",
  "last_name": "User",
  "role": "admin",
  "role_display": "Администратор",
  "discord_id": "123456789012345678",
  "discord_username": "admin#1234",
  "discord_avatar": "https://cdn.discordapp.com/avatars/123456789012345678/abcdef.png",
  "is_banned": false,
  "ban_reason": null,
  "date_joined": "2023-05-01T12:00:00Z",
  "last_login": "2023-05-20T15:30:00Z",
  "monthly_invites_limit": -1,
  "invites_used_this_month": 5,
  "available_invites": -1,
  "invited_by": "223e4567-e89b-12d3-a456-426614174001",
  "invited_by_username": "user1"
}
```

### Обновление пользователя

```
PATCH /api/users/{user_id}/update/
```

**Параметры запроса:**

```json
{
  "first_name": "New First Name",
  "last_name": "New Last Name",
  "email": "new.email@example.com",
  "role": "moderator",
  "monthly_invites_limit": 15
}
```

**Ответ:**

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "admin",
  "email": "new.email@example.com",
  "first_name": "New First Name",
  "last_name": "New Last Name",
  "role": "moderator",
  "role_display": "Модератор",
  "monthly_invites_limit": 15
  // ... другие поля
}
```

### Блокировка пользователя

```
POST /api/users/{user_id}/ban/
```

**Параметры запроса:**

```json
{
  "reason": "Нарушение правил"
}
```

**Ответ:**

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "admin",
  "is_banned": true,
  "ban_reason": "Нарушение правил"
  // ... другие поля
}
```

### Разблокировка пользователя

```
POST /api/users/{user_id}/unban/
```

**Ответ:**

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "admin",
  "is_banned": false,
  "ban_reason": null
  // ... другие поля
}
```

### Получение кода привязки Discord

```
POST /api/users/binding/code/
```

**Ответ:**

```json
{
  "code": "ABC123",
  "created_at": "2023-05-20T15:30:00Z",
  "expires_at": "2023-05-20T15:45:00Z",
  "is_used": false
}
```

### Привязка Discord-аккаунта

```
POST /api/users/binding/discord/
```

**Параметры запроса:**

```json
{
  "code": "ABC123",
  "discord_id": "123456789012345678",
  "discord_username": "username#1234",
  "discord_avatar": "https://cdn.discordapp.com/avatars/123456789012345678/abcdef.png"
}
```

**Ответ:**

```json
{
  "message": "Discord аккаунт успешно привязан",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "admin",
    "discord_id": "123456789012345678",
    "discord_username": "username#1234",
    "discord_avatar": "https://cdn.discordapp.com/avatars/123456789012345678/abcdef.png"
    // ... другие поля
  }
}
```

## Ключи

### Получение списка ключей

```
GET /api/keys/
```

**Параметры запроса:**
- `status` (опционально): Фильтр по статусу (active, used, expired, revoked)
- `type` (опционально): Фильтр по типу (standard, premium, lifetime)
- `created_by` (опционально): Фильтр по создателю
- `activated_by` (опционально): Фильтр по активировавшему пользователю

**Ответ:**

```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "key": "standard-1234-5678-9012",
    "key_type": "standard",
    "key_type_display": "Стандартный",
    "status": "active",
    "status_display": "Активный",
    "created_by": "223e4567-e89b-12d3-a456-426614174001",
    "created_by_username": "user1",
    "created_at": "2023-05-01T12:00:00Z",
    "activated_by": null,
    "activated_by_username": null,
    "activated_at": null,
    "duration_days": 30,
    "expires_at": null,
    "remaining_days": 30
  },
  {
    "id": "223e4567-e89b-12d3-a456-426614174001",
    "key": "premium-2345-6789-0123",
    "key_type": "premium",
    "key_type_display": "Премиум",
    "status": "used",
    "status_display": "Использован",
    "created_by": "123e4567-e89b-12d3-a456-426614174000",
    "created_by_username": "admin",
    "created_at": "2023-05-02T12:00:00Z",
    "activated_by": "223e4567-e89b-12d3-a456-426614174001",
    "activated_by_username": "user1",
    "activated_at": "2023-05-03T12:00:00Z",
    "duration_days": 90,
    "expires_at": "2023-08-01T12:00:00Z",
    "remaining_days": 75
  }
]
```

### Получение информации о ключе

```
GET /api/keys/{key_id}/
```

**Ответ:**

```json
{
  "key": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "key": "standard-1234-5678-9012",
    "key_type": "standard",
    "key_type_display": "Стандартный",
    "status": "active",
    "status_display": "Активный",
    "created_by": "223e4567-e89b-12d3-a456-426614174001",
    "created_by_username": "user1",
    "created_at": "2023-05-01T12:00:00Z",
    "activated_by": null,
    "activated_by_username": null,
    "activated_at": null,
    "duration_days": 30,
    "expires_at": null,
    "remaining_days": 30,
    "notes": "Тестовый ключ"
  },
  "history": [
    {
      "id": "323e4567-e89b-12d3-a456-426614174002",
      "action": "created",
      "action_display": "Создан",
      "user": "223e4567-e89b-12d3-a456-426614174001",
      "user_username": "user1",
      "timestamp": "2023-05-01T12:00:00Z",
      "details": "Создан ключ типа Стандартный с длительностью 30 дней"
    }
  ]
}
```

### Создание ключа

```
POST /api/keys/create/
```

**Параметры запроса:**

```json
{
  "key_type": "premium",
  "duration_days": 90,
  "notes": "Премиум ключ для VIP-клиента"
}
```

**Ответ:**

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "key": "premium-1234-5678-9012",
  "key_type": "premium",
  "key_type_display": "Премиум",
  "status": "active",
  "status_display": "Активный",
  "created_by": "223e4567-e89b-12d3-a456-426614174001",
  "created_by_username": "user1",
  "created_at": "2023-05-20T15:30:00Z",
  "duration_days": 90,
  "notes": "Премиум ключ для VIP-клиента"
  // ... другие поля
}
```

### Активация ключа

```
POST /api/keys/{key_id}/activate/
```

**Ответ:**

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "key": "premium-1234-5678-9012",
  "key_type": "premium",
  "key_type_display": "Премиум",
  "status": "used",
  "status_display": "Использован",
  "created_by": "223e4567-e89b-12d3-a456-426614174001",
  "created_by_username": "user1",
  "created_at": "2023-05-20T15:30:00Z",
  "activated_by": "123e4567-e89b-12d3-a456-426614174000",
  "activated_by_username": "admin",
  "activated_at": "2023-05-20T15:35:00Z",
  "duration_days": 90,
  "expires_at": "2023-08-18T15:35:00Z",
  "remaining_days": 90
  // ... другие поля
}
```

### Отзыв ключа

```
POST /api/keys/{key_id}/revoke/
```

**Ответ:**

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "key": "premium-1234-5678-9012",
  "key_type": "premium",
  "key_type_display": "Премиум",
  "status": "revoked",
  "status_display": "Отозван",
  // ... другие поля
}
```

## Инвайты

### Получение списка инвайтов

```
GET /api/invites/
```

**Параметры запроса:**
- `status` (опционально): Фильтр по статусу (active, used, expired, revoked)

**Ответ:**

```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "code": "ABCD-EFGH-IJKL",
    "created_by": "223e4567-e89b-12d3-a456-426614174001",
    "created_by_username": "user1",
    "created_at": "2023-05-01T12:00:00Z",
    "status": "active",
    "status_display": "Активный",
    "used_by": null,
    "used_by_username": null,
    "used_at": null,
    "used_ip": null,
    "expires_at": "2023-05-08T12:00:00Z",
    "is_active": true,
    "remaining_time": 168.0
  },
  {
    "id": "223e4567-e89b-12d3-a456-426614174001",
    "code": "MNOP-QRST-UVWX",
    "created_by": "123e4567-e89b-12d3-a456-426614174000",
    "created_by_username": "admin",
    "created_at": "2023-05-02T12:00:00Z",
    "status": "used",
    "status_display": "Использован",
    "used_by": "323e4567-e89b-12d3-a456-426614174002",
    "used_by_username": "user2",
    "used_at": "2023-05-03T12:00:00Z",
    "used_ip": "192.168.1.1",
    "expires_at": "2023-05-09T12:00:00Z",
    "is_active": false,
    "remaining_time": 0
  }
]
```

### Получение информации об инвайте

```
GET /api/invites/{invite_id}/
```

**Ответ:**

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "code": "ABCD-EFGH-IJKL",
  "created_by": "223e4567-e89b-12d3-a456-426614174001",
  "created_by_username": "user1",
  "created_at": "2023-05-01T12:00:00Z",
  "status": "active",
  "status_display": "Активный",
  "used_by": null,
  "used_by_username": null,
  "used_at": null,
  "used_ip": null,
  "expires_at": "2023-05-08T12:00:00Z",
  "is_active": true,
  "remaining_time": 168.0
}
```

### Создание инвайта

```
POST /api/invites/create/
```

**Параметры запроса:**

```json
{
  "expires_days": 14
}
```

**Ответ:**

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "code": "ABCD-EFGH-IJKL",
  "created_by": "223e4567-e89b-12d3-a456-426614174001",
  "created_by_username": "user1",
  "created_at": "2023-05-20T15:30:00Z",
  "status": "active",
  "status_display": "Активный",
  "expires_at": "2023-06-03T15:30:00Z",
  "is_active": true,
  "remaining_time": 336.0
  // ... другие поля
}
```

### Отзыв инвайта

```
POST /api/invites/{invite_id}/revoke/
```

**Ответ:**

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "code": "ABCD-EFGH-IJKL",
  "status": "revoked",
  "status_display": "Отозван",
  // ... другие поля
}
```

### Проверка валидности инвайт-кода

```
POST /api/invites/validate/
```

**Параметры запроса:**

```json
{
  "code": "ABCD-EFGH-IJKL"
}
```

**Ответ:**

```json
{
  "valid": true,
  "created_by": "user1"
}
```

## Логи

### Получение списка логов

```
GET /api/logs/
```

**Параметры запроса:**
- `level` (опционально): Фильтр по уровню (debug, info, warning, error, critical)
- `category` (опционально): Фильтр по категории (user, key, invite, discord, system, security)
- `user_id` (опционально): Фильтр по пользователю
- `ip_address` (опционально): Фильтр по IP-адресу
- `message` (опционально): Поиск по тексту сообщения
- `start_date` (опционально): Фильтр по начальной дате (формат: YYYY-MM-DD)
- `end_date` (опционально): Фильтр по конечной дате (формат: YYYY-MM-DD)

**Ответ:**

```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "timestamp": "2023-05-20T15:30:00Z",
    "level": "info",
    "level_display": "Информация",
    "category": "user",
    "category_display": "Пользователи",
    "message": "Пользователь user1 создал инвайт ABCD-EFGH-IJKL",
    "user": "223e4567-e89b-12d3-a456-426614174001",
    "username": "user1",
    "ip_address": "192.168.1.1",
    "extra_data": null
  },
  {
    "id": "223e4567-e89b-12d3-a456-426614174001",
    "timestamp": "2023-05-20T15:35:00Z",
    "level": "info",
    "level_display": "Информация",
    "category": "key",
    "category_display": "Ключи",
    "message": "Пользователь admin создал ключ premium-1234-5678-9012",
    "user": "123e4567-e89b-12d3-a456-426614174000",
    "username": "admin",
    "ip_address": "192.168.1.2",
    "extra_data": null
  }
]
```

### Получение информации о логе

```
GET /api/logs/{log_id}/
```

**Ответ:**

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "timestamp": "2023-05-20T15:30:00Z",
  "level": "info",
  "level_display": "Информация",
  "category": "user",
  "category_display": "Пользователи",
  "message": "Пользователь user1 создал инвайт ABCD-EFGH-IJKL",
  "user": "223e4567-e89b-12d3-a456-426614174001",
  "username": "user1",
  "ip_address": "192.168.1.1",
  "extra_data": {
    "invite_code": "ABCD-EFGH-IJKL",
    "expires_at": "2023-05-27T15:30:00Z"
  }
}
```

## Ошибки и коды ответов

| Код | Описание |
|-----|----------|
| 200 | OK - Запрос успешно выполнен |
| 201 | Created - Ресурс успешно создан |
| 400 | Bad Request - Ошибка в запросе |
| 401 | Unauthorized - Отсутствует или неверный токен аутентификации |
| 403 | Forbidden - Нет прав на выполнение действия |
| 404 | Not Found - Ресурс не найден |
| 500 | Internal Server Error - Внутренняя ошибка сервера |

### Формат ошибок

```json
{
  "error": "Описание ошибки",
  "field_name": ["Ошибка в поле"]
}
```

## WebSocket API

### Подключение

```
ws://your-domain.com/ws/keys/status/
ws://your-domain.com/ws/users/status/
```

### События

#### Обновление статуса ключа

```json
{
  "type": "key_status_update",
  "key_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "used",
  "action": "status_changed",
  "timestamp": "2023-05-20T15:35:00Z"
}
```

#### Обновление статуса пользователя

```json
{
  "type": "user_status_update",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "online",
  "timestamp": "2023-05-20T15:30:00Z"
}
``` 