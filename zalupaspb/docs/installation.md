# Установка и настройка ZalupaSPB

Данный документ содержит подробные инструкции по установке и настройке системы ZalupaSPB.

## Системные требования

- **Операционная система**: Ubuntu 22.04 LTS (рекомендуется) или другие Linux-дистрибутивы
- **Python**: 3.10 или выше
- **PostgreSQL**: 14.0 или выше
- **Redis**: 6.0 или выше
- **Nginx**: 1.18 или выше (для продакшн-окружения)
- **Certbot**: Для настройки SSL (для продакшн-окружения)

## Подготовка системы

### Установка зависимостей

```bash
# Обновление системы
sudo apt update
sudo apt upgrade -y

# Установка необходимых пакетов
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib redis-server nginx

# Установка Certbot (для HTTPS)
sudo apt install -y certbot python3-certbot-nginx
```

### Настройка PostgreSQL

```bash
# Создание пользователя для базы данных
sudo -u postgres createuser -P zalupaspb
# Введите пароль для нового пользователя

# Создание базы данных
sudo -u postgres createdb -O zalupaspb zalupaspb
```

### Настройка Redis

Redis обычно работает с настройками по умолчанию, но можно проверить его статус:

```bash
sudo systemctl status redis-server
```

## Установка ZalupaSPB

### Клонирование репозитория

```bash
git clone https://github.com/your-username/zalupaspb.git
cd zalupaspb
```

### Настройка виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate
```

### Установка зависимостей проекта

```bash
pip install -r zalupaspb/web/requirements.txt
pip install -r zalupaspb/bot/requirements.txt
```

### Настройка конфигурации

1. Скопируйте примеры конфигурационных файлов:

```bash
cp zalupaspb/config/config.yaml.example zalupaspb/config/config.yaml
cp zalupaspb/config/env.example zalupaspb/config/.env
```

2. Отредактируйте файл `.env`, указав настройки базы данных и Discord:

```bash
nano zalupaspb/config/.env
```

Обязательные параметры для изменения:
- `DJANGO_SECRET_KEY`: Уникальный секретный ключ для Django
- `DB_PASSWORD`: Пароль пользователя базы данных
- `DISCORD_BOT_TOKEN`: Токен Discord-бота
- `DISCORD_GUILD_ID`: ID сервера Discord
- `DISCORD_*_ROLE_ID`: ID ролей на сервере Discord

3. Отредактируйте файл `config.yaml`:

```bash
nano zalupaspb/config/config.yaml
```

Установите корректные ID ролей и каналов Discord.

### Запуск скрипта инициализации

Скрипт инициализации автоматизирует большую часть процесса настройки:

```bash
bash zalupaspb/scripts/init.sh
```

Скрипт выполнит следующие действия:
- Создаст виртуальное окружение Python
- Установит зависимости
- Проверит наличие конфигурационных файлов
- Создаст базу данных (опционально)
- Выполнит миграции Django
- Создаст суперпользователя (опционально)
- Настроит Nginx (опционально)
- Настроит SSL с Certbot (опционально)
- Настроит systemd-сервисы (опционально)

## Запуск в режиме разработки

### Запуск веб-приложения

```bash
cd zalupaspb/web
python manage.py runserver 0.0.0.0:8000
```

### Запуск Discord-бота

```bash
cd zalupaspb/bot
python bot.py
```

## Настройка для продакшн-окружения

### Настройка Nginx

Если вы не использовали скрипт инициализации для настройки Nginx, создайте конфигурационный файл вручную:

```bash
sudo nano /etc/nginx/sites-available/zalupaspb
```

Содержимое файла:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location /static/ {
        alias /path/to/zalupaspb/web/staticfiles/;
    }

    location /media/ {
        alias /path/to/zalupaspb/web/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Активируйте конфигурацию:

```bash
sudo ln -s /etc/nginx/sites-available/zalupaspb /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Настройка SSL с Certbot

```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### Настройка Gunicorn и systemd

Создайте сервис для веб-приложения:

```bash
sudo nano /etc/systemd/system/zalupaspb-web.service
```

Содержимое файла:

```ini
[Unit]
Description=ZalupaSPB Web Service
After=network.target

[Service]
User=your-username
Group=your-username
WorkingDirectory=/path/to/zalupaspb/web
ExecStart=/path/to/zalupaspb/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 zalupaspb.wsgi:application
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Создайте сервис для Discord-бота:

```bash
sudo nano /etc/systemd/system/zalupaspb-bot.service
```

Содержимое файла:

```ini
[Unit]
Description=ZalupaSPB Discord Bot
After=network.target

[Service]
User=your-username
Group=your-username
WorkingDirectory=/path/to/zalupaspb/bot
ExecStart=/path/to/zalupaspb/venv/bin/python bot.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Активируйте и запустите сервисы:

```bash
sudo systemctl daemon-reload
sudo systemctl enable zalupaspb-web.service zalupaspb-bot.service
sudo systemctl start zalupaspb-web.service zalupaspb-bot.service
```

## Проверка работоспособности

### Проверка веб-приложения

Откройте в браузере адрес `http://your-domain.com` или `http://localhost:8000` (в режиме разработки).
Вы должны увидеть страницу входа ZalupaSPB.

### Проверка Discord-бота

В Discord выполните команду `/stats`. Если бот ответит, значит он работает корректно.

## Возможные проблемы и их решение

### Ошибка подключения к базе данных

1. Проверьте настройки в файле `.env`
2. Убедитесь, что PostgreSQL запущен: `sudo systemctl status postgresql`
3. Проверьте доступность базы данных: `sudo -u postgres psql -c "SELECT 1" zalupaspb`

### Бот не запускается

1. Проверьте токен в файле `.env`
2. Убедитесь, что у бота есть необходимые разрешения на сервере Discord
3. Проверьте лог ошибок: `cat zalupaspb/bot/bot.log`

### Проблемы с WebSocket

1. Убедитесь, что Redis запущен: `sudo systemctl status redis-server`
2. Проверьте настройки ASGI в файле `zalupaspb/web/zalupaspb/asgi.py`
3. Проверьте конфигурацию Nginx для WebSocket (в продакшн-окружении)

## Дополнительная информация

Более подробную информацию о работе с системой можно найти в следующих документах:
- [API Reference](api.md)
- [Руководство пользователя](user-guide.md)
- [Руководство администратора](admin-guide.md) 