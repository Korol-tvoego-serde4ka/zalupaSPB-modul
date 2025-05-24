# Руководство по развертыванию ZalupaSPB на dinozavrikgugl.ru

## Предварительные требования

1. Сервер Ubuntu 22.04.5 LTS или выше
2. Домен dinozavrikgugl.ru, направленный на IP вашего сервера
3. Python 3.10+
4. PostgreSQL 14+
5. Redis 6+
6. Nginx

## Шаг 1: Клонирование проекта

```bash
git clone https://github.com/your-username/zalupaspb.git
cd zalupaspb
```

## Шаг 2: Настройка окружения

### Создание конфигурационных файлов

```bash
# Создаем конфигурационные файлы из примеров
cp zalupaspb/config/env.example zalupaspb/config/.env
cp zalupaspb/config/config.yaml.example zalupaspb/config/config.yaml

# Редактируем .env файл (замените значения на свои)
nano zalupaspb/config/.env
```

Настройте `.env` файл, заменив значения по умолчанию на свои:
- `DJANGO_SECRET_KEY` - используйте случайную строку для ключа
- `DJANGO_ALLOWED_HOSTS` - убедитесь, что включен dinozavrikgugl.ru
- `DB_PASSWORD` - установите надежный пароль для базы данных
- `DISCORD_BOT_TOKEN` - ваш токен бота Discord
- `DISCORD_GUILD_ID`, `DISCORD_*_ROLE_ID` - ID сервера и ролей Discord

### Настройка файла config.yaml

```bash
# Редактируем config.yaml
nano zalupaspb/config/config.yaml
```

Обновите конфигурацию Discord с вашими ID ролей и каналов.

## Шаг 3: Установка зависимостей

```bash
# Создаем виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Устанавливаем зависимости
pip install -r zalupaspb/web/requirements.txt
pip install -r zalupaspb/bot/requirements.txt
pip install channels_redis  # Добавляем недостающую зависимость
```

## Шаг 4: Настройка базы данных

```bash
# Создаем базу данных PostgreSQL
sudo -u postgres psql -c "CREATE DATABASE zalupaspb;"
sudo -u postgres psql -c "CREATE USER zalupaspb WITH PASSWORD 'ваш_надежный_пароль';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE zalupaspb TO zalupaspb;"

# Обновляем настройки в .env файле
sed -i "s/DB_NAME=.*/DB_NAME=zalupaspb/" zalupaspb/config/.env
sed -i "s/DB_USER=.*/DB_USER=zalupaspb/" zalupaspb/config/.env
sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=ваш_надежный_пароль/" zalupaspb/config/.env
```

## Шаг 5: Настройка Django

```bash
# Переходим в директорию веб-приложения
cd zalupaspb/web

# Выполняем миграции
python manage.py migrate

# Создаем суперпользователя
python manage.py createsuperuser

# Собираем статические файлы
python manage.py collectstatic --noinput

# Возвращаемся в корневую директорию проекта
cd ../..
```

## Шаг 6: Генерация токенов для API бота

```bash
# Создаем пользователя для бота и генерируем токены
python zalupaspb/scripts/generate_tokens.py discord_bot ваш_надежный_пароль_для_бота
```

Этот скрипт создаст пользователя для бота и сгенерирует токены доступа и обновления,
которые автоматически будут сохранены в .env файл.

## Шаг 7: Настройка Nginx

```bash
# Копируем пример конфигурации Nginx
sudo cp zalupaspb/config/nginx-example.conf /etc/nginx/sites-available/dinozavrikgugl.ru.conf

# Редактируем конфигурацию с нужными путями
sudo nano /etc/nginx/sites-available/dinozavrikgugl.ru.conf
```

Замените `/path/to/zalupaspb` на реальный путь к вашему проекту.

```bash
# Активируем конфигурацию
sudo ln -s /etc/nginx/sites-available/dinozavrikgugl.ru.conf /etc/nginx/sites-enabled/
sudo nginx -t  # Проверяем конфигурацию
sudo systemctl restart nginx
```

## Шаг 8: Настройка Gunicorn и systemd

### Создание службы для веб-приложения

```bash
sudo bash -c "cat > /etc/systemd/system/zalupaspb-web.service << EOL
[Unit]
Description=ZalupaSPB Web Service
After=network.target

[Service]
User=$(whoami)
Group=$(id -gn)
WorkingDirectory=$(pwd)/zalupaspb/web
ExecStart=$(pwd)/venv/bin/gunicorn -k uvicorn.workers.UvicornWorker zalupaspb.asgi:application --workers 3 --bind 127.0.0.1:8000
Restart=on-failure
RestartSec=5
Environment=\"DJANGO_SETTINGS_MODULE=zalupaspb.settings\"

[Install]
WantedBy=multi-user.target
EOL"
```

### Создание службы для Discord бота

```bash
sudo bash -c "cat > /etc/systemd/system/zalupaspb-bot.service << EOL
[Unit]
Description=ZalupaSPB Discord Bot Service
After=network.target zalupaspb-web.service

[Service]
User=$(whoami)
Group=$(id -gn)
WorkingDirectory=$(pwd)/zalupaspb/bot
ExecStart=$(pwd)/venv/bin/python bot.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL"
```

### Активация и запуск служб

```bash
sudo systemctl daemon-reload
sudo systemctl enable zalupaspb-web.service
sudo systemctl enable zalupaspb-bot.service
sudo systemctl start zalupaspb-web.service
sudo systemctl start zalupaspb-bot.service
```

## Шаг 9: Проверка и отладка

### Проверка статуса служб

```bash
sudo systemctl status zalupaspb-web.service
sudo systemctl status zalupaspb-bot.service
```

### Проверка логов

```bash
# Логи веб-приложения
sudo journalctl -u zalupaspb-web.service -f

# Логи Discord бота
sudo journalctl -u zalupaspb-bot.service -f

# Логи Nginx
sudo tail -f /var/log/nginx/dinozavrikgugl.ru.error.log
```

## Решение проблем с CORS

Если у вас возникают проблемы с CORS (как в скриншоте с ошибкой 400 Bad Request), убедитесь, что:

1. В настройках Django правильно настроен CORS:
   ```python
   CORS_ALLOWED_ORIGINS = ['https://dinozavrikgugl.ru', 'https://www.dinozavrikgugl.ru']
   ```

2. В конфигурации Nginx правильно настроены заголовки CORS:
   ```nginx
   add_header 'Access-Control-Allow-Origin' 'https://dinozavrikgugl.ru' always;
   add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS, PUT, DELETE' always;
   add_header 'Access-Control-Allow-Headers' 'Origin, X-Requested-With, Content-Type, Accept, Authorization' always;
   ```

3. Добавьте специальную обработку для Cross-Origin-Opener-Policy:
   ```nginx
   # Добавьте в секцию server в конфигурации Nginx
   add_header Cross-Origin-Opener-Policy "same-origin-allow-popups" always;
   add_header Cross-Origin-Resource-Policy "cross-origin" always;
   ```

## Обновление проекта

Для обновления проекта выполните следующие шаги:

```bash
# Обновляем код из репозитория
git pull

# Активируем виртуальное окружение
source venv/bin/activate

# Обновляем зависимости
pip install -r zalupaspb/web/requirements.txt
pip install -r zalupaspb/bot/requirements.txt

# Применяем миграции
cd zalupaspb/web
python manage.py migrate
python manage.py collectstatic --noinput

# Перезапускаем службы
sudo systemctl restart zalupaspb-web.service
sudo systemctl restart zalupaspb-bot.service
``` 