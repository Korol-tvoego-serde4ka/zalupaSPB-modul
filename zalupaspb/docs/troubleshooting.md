# Руководство по решению проблем ZalupaSPB

В этом документе собраны решения для наиболее распространенных проблем, с которыми вы можете столкнуться при установке, настройке и использовании ZalupaSPB.

## Проблемы с запуском и настройкой

### Проблема: Django возвращает 400 Bad Request

**Симптомы**: При попытке доступа к API или веб-интерфейсу вы получаете ошибку 400 Bad Request.

**Решение**:
1. Проверьте `ALLOWED_HOSTS` в `settings.py`:
   ```python
   ALLOWED_HOSTS = ['dinozavrikgugl.ru', 'www.dinozavrikgugl.ru', 'localhost', '127.0.0.1']
   ```

2. Проверьте `CSRF_TRUSTED_ORIGINS` для корректной работы CSRF-защиты:
   ```python
   CSRF_TRUSTED_ORIGINS = ['https://dinozavrikgugl.ru', 'https://www.dinozavrikgugl.ru']
   ```

3. При использовании Nginx убедитесь, что правильно настроены заголовки:
   ```nginx
   proxy_set_header Host $host;
   proxy_set_header X-Real-IP $remote_addr;
   proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
   proxy_set_header X-Forwarded-Proto $scheme;
   ```

### Проблема: Статические файлы не загружаются

**Симптомы**: Веб-страницы отображаются без стилей, JavaScript не работает.

**Решение**:
1. Выполните команду для сбора статических файлов:
   ```bash
   python manage.py collectstatic --noinput
   ```

2. Проверьте настройки статических файлов в `settings.py`:
   ```python
   STATIC_URL = 'static/'
   STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
   STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
   ```

3. В конфигурации Nginx убедитесь, что указан правильный путь:
   ```nginx
   location /static/ {
       alias /путь/к/zalupaspb/web/staticfiles/;
   }
   ```

4. Проверьте права доступа к директориям:
   ```bash
   sudo chown -R www-data:www-data /путь/к/zalupaspb/web/staticfiles
   sudo chmod -R 755 /путь/к/zalupaspb/web/staticfiles
   ```

### Проблема: Discord-бот не подключается

**Симптомы**: Бот запускается, но не реагирует на команды или выдает ошибки.

**Решение**:
1. Проверьте правильность токена Discord в `.env` файле:
   ```
   DISCORD_BOT_TOKEN=ваш_токен_бота
   ```

2. Убедитесь, что указаны правильные ID сервера и ролей:
   ```
   DISCORD_GUILD_ID=ваш_id_сервера
   DISCORD_ADMIN_ROLE_ID=id_роли_админа
   DISCORD_MODERATOR_ROLE_ID=id_роли_модератора
   DISCORD_USER_ROLE_ID=id_роли_пользователя
   ```

3. Проверьте, есть ли у бота необходимые разрешения на сервере Discord.

4. Проверьте, что API доступен для бота:
   ```bash
   curl -I http://localhost:8000/api/docs/
   ```

5. Проверьте логи бота:
   ```bash
   tail -f /var/log/zalupaspb-bot.log
   ```

## Проблемы с функциональностью

### Проблема: Инвайты не работают

**Симптомы**: Пользователи не могут зарегистрироваться по инвайтам.

**Решение**:
1. Проверьте, что инвайты активны в базе данных:
   ```sql
   SELECT * FROM invites_invite WHERE is_used = false;
   ```

2. Убедитесь, что лимиты инвайтов настроены правильно:
   ```python
   # settings.py
   INVITE_LIMITS = {
       'admin': -1,  # бесконечно
       'moderator': 10,
       'user': 2,
       'support': 0,
   }
   ```

3. Проверьте, не достигли ли пользователи своего лимита инвайтов:
   ```sql
   SELECT user_id, COUNT(*) FROM invites_invite WHERE created_at > (NOW() - INTERVAL '1 month') GROUP BY user_id;
   ```

### Проблема: Ключи не активируются

**Симптомы**: Пользователи не могут активировать ключи доступа.

**Решение**:
1. Проверьте статус ключей в базе данных:
   ```sql
   SELECT * FROM keys_key WHERE code = 'проблемный_код';
   ```

2. Убедитесь, что ключ не был уже использован:
   ```sql
   SELECT * FROM keys_key WHERE code = 'проблемный_код' AND is_active = true AND user_id IS NULL;
   ```

3. Проверьте работу API-эндпоинта активации ключей:
   ```bash
   curl -X POST http://localhost:8000/api/keys/activate/ -H "Content-Type: application/json" -d '{"code":"тестовый_код"}'
   ```

4. Проверьте логи для выявления ошибок:
   ```bash
   tail -f /var/log/zalupaspb.log
   ```

### Проблема: Не работает синхронизация ролей с Discord

**Симптомы**: При изменении роли пользователя на сайте, роль не обновляется в Discord.

**Решение**:
1. Убедитесь, что бот имеет права для управления ролями на сервере Discord.

2. Проверьте, правильно ли настроены ID ролей в `config.yaml`:
   ```yaml
   discord:
     roles:
       admin: "ID_роли_админа"
       moderator: "ID_роли_модератора"
       user: "ID_роли_пользователя"
       support: "ID_роли_поддержки"
   ```

3. Проверьте, привязан ли Discord-аккаунт пользователя к его аккаунту на сайте:
   ```sql
   SELECT * FROM users_user WHERE discord_id IS NOT NULL;
   ```

4. Проверьте логи бота для выявления ошибок:
   ```bash
   tail -f /var/log/zalupaspb-bot.log
   ```

## Проблемы безопасности

### Проблема: Множественная регистрация с одного Discord-аккаунта

**Симптомы**: Пользователи обходят ограничение и регистрируют несколько аккаунтов с одного Discord-аккаунта.

**Решение**:
1. Убедитесь, что включена проверка на уникальность Discord ID:
   ```python
   # users/models.py
   discord_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
   ```

2. Проверьте базу данных на дубликаты:
   ```sql
   SELECT discord_id, COUNT(*) FROM users_user WHERE discord_id IS NOT NULL GROUP BY discord_id HAVING COUNT(*) > 1;
   ```

3. Добавьте дополнительную проверку на уровне API:
   ```python
   # В вашем представлении для регистрации
   if User.objects.filter(discord_id=discord_id).exists():
       return Response({"error": "Discord аккаунт уже привязан к другому пользователю"}, status=400)
   ```

### Проблема: Нарушение квот инвайтов

**Симптомы**: Пользователи создают больше инвайтов, чем разрешено их ролью.

**Решение**:
1. Проверьте, корректно ли настроены квоты в `settings.py`:
   ```python
   INVITE_LIMITS = {
       'admin': -1,  # бесконечно
       'moderator': 10,
       'user': 2,
       'support': 0,
   }
   ```

2. Добавьте дополнительную проверку на создание инвайтов:
   ```python
   # В вашем представлении для создания инвайтов
   if used_invites >= invite_limit and invite_limit != -1:
       return Response({"error": "Вы достигли лимита инвайтов на этот месяц"}, status=400)
   ```

3. Мониторьте создание инвайтов через логи:
   ```sql
   SELECT user_id, COUNT(*) FROM invites_invite WHERE created_at > (NOW() - INTERVAL '1 month') GROUP BY user_id ORDER BY COUNT(*) DESC;
   ```

## Оптимизация производительности

### Проблема: Медленная загрузка страниц

**Симптомы**: Страницы загружаются долго, особенно при большом количестве пользователей.

**Решение**:
1. Оптимизируйте запросы к базе данных:
   - Используйте `select_related()` и `prefetch_related()` для уменьшения количества запросов
   - Добавьте индексы для часто используемых полей

2. Настройте кэширование:
   ```python
   # settings.py
   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.redis.RedisCache',
           'LOCATION': 'redis://127.0.0.1:6379/1',
       }
   }
   ```

3. Настройте Nginx для кэширования статических файлов:
   ```nginx
   location /static/ {
       alias /путь/к/zalupaspb/web/staticfiles/;
       expires 30d;
       add_header Cache-Control "public, max-age=2592000";
   }
   ```

4. Увеличьте количество рабочих процессов Gunicorn:
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker zalupaspb.asgi:application
   ```

## Полезные скрипты и команды

### Проверка состояния системы

```bash
#!/bin/bash
echo "Проверка состояния системы ZalupaSPB"
echo "---------------------------------"
echo "Проверка сервисов:"
systemctl status zalupaspb-web.service | grep Active
systemctl status zalupaspb-bot.service | grep Active
systemctl status nginx | grep Active
systemctl status postgresql | grep Active
systemctl status redis-server | grep Active

echo "---------------------------------"
echo "Статистика базы данных:"
echo "Количество пользователей: $(sudo -u postgres psql -d zalupaspb -c "SELECT COUNT(*) FROM users_user;" -t)"
echo "Активные ключи: $(sudo -u postgres psql -d zalupaspb -c "SELECT COUNT(*) FROM keys_key WHERE is_active = true;" -t)"
echo "Неиспользованные инвайты: $(sudo -u postgres psql -d zalupaspb -c "SELECT COUNT(*) FROM invites_invite WHERE is_used = false;" -t)"

echo "---------------------------------"
echo "Проверка соединения с Discord API:"
curl --silent -o /dev/null -w "%{http_code}" https://discord.com/api/v9/gateway
echo " (код ответа Discord API)"

echo "---------------------------------"
echo "Проверка доступности веб-интерфейса:"
curl --silent -o /dev/null -w "%{http_code}" http://localhost:8000/
echo " (код ответа веб-интерфейса)"
```

### Генерация тестовых ключей

```python
#!/usr/bin/env python
import os
import sys
import django

# Настройка Django
sys.path.append('/путь/к/zalupaspb/web')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zalupaspb.settings')
django.setup()

from keys.models import Key
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.utils import timezone
import random
import string

User = get_user_model()

def generate_key_code(length=16):
    """Генерирует случайный код ключа"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def generate_keys(count=5, key_type='standard', days=30):
    """Генерирует ключи указанного типа"""
    admin = User.objects.filter(is_superuser=True).first()
    
    if not admin:
        print("Не найден администратор для создания ключей")
        return
    
    expiry_date = None
    if days > 0:
        expiry_date = timezone.now() + timedelta(days=days)
    
    created_keys = []
    
    for _ in range(count):
        code = generate_key_code()
        key = Key.objects.create(
            code=code,
            type=key_type,
            created_by=admin,
            expiry_date=expiry_date,
            is_active=True
        )
        created_keys.append(key.code)
    
    return created_keys

if __name__ == "__main__":
    count = 5
    key_type = 'standard'
    days = 30
    
    if len(sys.argv) > 1:
        count = int(sys.argv[1])
    if len(sys.argv) > 2:
        key_type = sys.argv[2]
    if len(sys.argv) > 3:
        days = int(sys.argv[3])
    
    keys = generate_keys(count, key_type, days)
    
    if keys:
        print(f"Сгенерировано {len(keys)} ключей типа {key_type} на {days} дней:")
        for key in keys:
            print(key)
    else:
        print("Не удалось создать ключи")
```

## Заключение

Данное руководство покрывает наиболее распространенные проблемы, с которыми вы можете столкнуться при работе с ZalupaSPB. Если проблема не описана в этом документе, рекомендуем:

1. Проверить логи всех компонентов системы
2. Проверить конфигурационные файлы на наличие ошибок
3. Проверить права доступа к файлам и директориям
4. Проверить сетевые соединения и настройки файрвола

В случае серьезных проблем рекомендуем обратиться к разработчикам через GitHub Issues или Discord-сервер поддержки. 