# ZalupaSPB

## Описание проекта
ZalupaSPB - система управления доступом к сервисам через инвайты и ключи с интеграцией Discord. Основные возможности:

- Регистрация пользователей только по инвайтам от существующих пользователей
- Генерация и активация ключей доступа с разными сроками действия
- Интеграция с Discord для синхронизации ролей и управления доступом
- Система квот инвайтов в зависимости от роли пользователя
- Полное логирование действий пользователей
- Загрузка и управление версиями лоадера

## Архитектура
Проект состоит из следующих компонентов:
- Веб-приложение (Django + DRF)
- Discord-бот (discord.py)
- Единая база данных (PostgreSQL)
- Система кеширования (Redis)
- WebSocket для обновлений в реальном времени

## Структура проекта
```
zalupaSPB-modul/
├── README.md               # Основной README проекта
├── nginx/                  # Конфигурация Nginx
│   └── zalupaspb.conf      # Конфигурационный файл для сервера
├── zalupaspb/             
│   ├── web/                # Django веб-приложение
│   │   ├── zalupaspb/      # Основной проект Django
│   │   ├── users/          # Приложение для работы с пользователями
│   │   ├── keys/           # Приложение для работы с ключами
│   │   ├── invites/        # Приложение для работы с инвайтами
│   │   ├── logs/           # Приложение для логирования
│   │   ├── static/         # Статические файлы
│   │   ├── templates/      # HTML шаблоны
│   │   ├── media/          # Загружаемые файлы
│   │   ├── manage.py       # Скрипт управления Django
│   │   └── requirements.txt # Зависимости Python
│   ├── bot/                # Discord бот
│   │   ├── bot.py          # Основной файл бота
│   │   └── api_client.py   # Клиент для работы с API
│   ├── config/             # Конфигурационные файлы
│   │   ├── config.yaml.example # Пример основной конфигурации
│   │   ├── env.example      # Пример переменных окружения
│   │   └── nginx-example.conf # Пример конфигурации Nginx
│   ├── docs/               # Документация
│   └── scripts/            # Скрипты для установки и управления
```

## Установка

### 1. Требования
- Python 3.10+
- PostgreSQL 14+
- Redis 6+
- Nginx (для продакшн)
- Certbot (для HTTPS)

### 2. Клонирование репозитория
```bash
git clone https://github.com/your-username/zalupaspb.git
cd zalupaspb
```

### 3. Настройка конфигурации
1. Создайте конфигурационные файлы из примеров:
```bash
cp zalupaspb/config/env.example zalupaspb/config/.env
cp zalupaspb/config/config.yaml.example zalupaspb/config/config.yaml
```

2. Отредактируйте файл `.env` и установите правильные значения для:
   - DJANGO_SECRET_KEY (сгенерируйте новый секретный ключ)
   - DB_PASSWORD (установите пароль PostgreSQL)
   - DISCORD_BOT_TOKEN (токен вашего Discord-бота)
   - DISCORD_GUILD_ID (ID вашего сервера Discord)
   - DISCORD_*_ROLE_ID (ID ролей на вашем Discord-сервере)

### 4. Установка и настройка базы данных
1. Установите PostgreSQL:
```bash
sudo apt install postgresql postgresql-contrib
```

2. Создайте базу данных и пользователя:
```bash
sudo -u postgres psql -c "CREATE USER zalupaspb WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "CREATE DATABASE zalupaspb OWNER zalupaspb;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE zalupaspb TO zalupaspb;"
```

### 5. Установка Redis
```bash
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### 6. Установка зависимостей Python
```bash
cd zalupaspb/web
python -m venv venv
source venv/bin/activate  # В Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 7. Настройка Django
1. Применение миграций базы данных:
```bash
python manage.py migrate
```

2. Создание суперпользователя (администратора):
```bash
python manage.py createsuperuser
```

3. Сбор статических файлов:
```bash
python manage.py collectstatic
```

### 8. Настройка Nginx
1. Создайте файл конфигурации для Nginx:
```bash
sudo cp nginx/zalupaspb.conf /etc/nginx/sites-available/zalupaspb.conf
sudo ln -s /etc/nginx/sites-available/zalupaspb.conf /etc/nginx/sites-enabled/
```

2. Отредактируйте пути в конфигурационном файле, если необходимо.

3. Перезапустите Nginx:
```bash
sudo systemctl restart nginx
```

### 9. Запуск приложения

#### Разработка
```bash
# Запуск веб-сервера
cd zalupaspb/web
python manage.py runserver

# Запуск бота (в отдельном терминале)
cd zalupaspb/bot
python bot.py
```

#### Продакшн
1. Установите gunicorn:
```bash
pip install gunicorn
```

2. Создайте службы systemd для автоматического запуска:

**zalupaspb-web.service:**
```ini
[Unit]
Description=ZalupaSPB Web Service
After=network.target postgresql.service redis-server.service

[Service]
User=your_user
Group=your_group
WorkingDirectory=/path/to/zalupaspb/web
ExecStart=/path/to/zalupaspb/web/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 zalupaspb.wsgi:application
Restart=on-failure
Environment="PYTHONPATH=/path/to/zalupaspb"

[Install]
WantedBy=multi-user.target
```

**zalupaspb-bot.service:**
```ini
[Unit]
Description=ZalupaSPB Discord Bot Service
After=network.target zalupaspb-web.service

[Service]
User=your_user
Group=your_group
WorkingDirectory=/path/to/zalupaspb/bot
ExecStart=/path/to/zalupaspb/web/venv/bin/python bot.py
Restart=on-failure
Environment="PYTHONPATH=/path/to/zalupaspb"

[Install]
WantedBy=multi-user.target
```

3. Активируйте и запустите службы:
```bash
sudo systemctl enable zalupaspb-web.service zalupaspb-bot.service
sudo systemctl start zalupaspb-web.service zalupaspb-bot.service
```

## Устранение проблем

### Ошибка 500 при регистрации
1. Проверьте логи Django:
```bash
tail -f zalupaspb/web/logs/django.log
```

2. Частые причины:
   - Неверные настройки базы данных в `.env`
   - Отсутствие Redis (необходим для WebSocket и кеширования)
   - Ошибки в конфигурации Discord-бота

### Профиль пользователя не отображается (ошибка 404)
1. Проверьте, что URL-адреса настроены корректно:
```bash
python manage.py show_urls
```

2. Возможные решения:
   - Проверьте наличие необходимых URL-шаблонов в `zalupaspb/web/zalupaspb/urls.py`
   - Убедитесь, что представление для профиля пользователя корректно определено

## Документация
Подробная документация доступна в папке `docs/`:
- [Установка и настройка](zalupaspb/docs/installation.md)
- [API Reference](zalupaspb/docs/api.md)
- [Руководство пользователя](zalupaspb/docs/user-guide.md)
- [Руководство администратора](zalupaspb/docs/admin-guide.md)

## Лицензия
Этот проект распространяется под закрытой лицензией и предназначен только для внутреннего использования. 
