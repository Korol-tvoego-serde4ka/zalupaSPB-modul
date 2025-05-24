#!/bin/bash
# Скрипт инициализации проекта ZalupaSPB

# Определение OS
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    WINDOWS=true
else
    WINDOWS=false
fi

# Цвета для вывода (не Windows)
if [ "$WINDOWS" = false ]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[0;33m'
    NC='\033[0m' # No Color
else
    GREEN=''
    RED=''
    YELLOW=''
    NC=''
fi

echo -e "${GREEN}Начинаем установку ZalupaSPB...${NC}"

# Проверяем, находимся ли мы в корневой директории проекта
if [ ! -d "zalupaspb" ]; then
    echo -e "${RED}Ошибка: Запустите скрипт из корневой директории проекта${NC}"
    exit 1
fi

# Создаем виртуальное окружение Python
echo -e "${YELLOW}Создаем виртуальное окружение Python...${NC}"
if [ "$WINDOWS" = true ]; then
    python -m venv venv
    venv\\Scripts\\activate
else
    python3 -m venv venv
    source venv/bin/activate
fi

# Устанавливаем зависимости
echo -e "${YELLOW}Устанавливаем зависимости...${NC}"
pip install -r zalupaspb/web/requirements.txt
pip install -r zalupaspb/bot/requirements.txt

# Проверяем конфигурационные файлы
echo -e "${YELLOW}Проверяем конфигурационные файлы...${NC}"
if [ ! -f "zalupaspb/config/config.yaml" ]; then
    echo -e "${YELLOW}Файл config.yaml не найден, создаем из примера...${NC}"
    if [ "$WINDOWS" = true ]; then
        copy zalupaspb\\config\\config.yaml.example zalupaspb\\config\\config.yaml
    else
        cp zalupaspb/config/config.yaml.example zalupaspb/config/config.yaml
    fi
    echo -e "${RED}Важно: Отредактируйте файл zalupaspb/config/config.yaml!${NC}"
fi

if [ ! -f "zalupaspb/config/.env" ]; then
    echo -e "${YELLOW}Файл .env не найден, создаем из примера...${NC}"
    if [ "$WINDOWS" = true ]; then
        copy zalupaspb\\config\\env.example zalupaspb\\config\\.env
    else
        cp zalupaspb/config/env.example zalupaspb/config/.env
    fi
    echo -e "${RED}Важно: Отредактируйте файл zalupaspb/config/.env!${NC}"
fi

# Создаем базу данных PostgreSQL (только для Linux)
if [ "$WINDOWS" = false ]; then
    echo -e "${YELLOW}Настройка базы данных...${NC}"
    read -p "Создать базу данных PostgreSQL? (y/n): " create_db
    if [ "$create_db" = "y" ]; then
        read -p "Имя базы данных (default: zalupaspb): " db_name
        db_name=${db_name:-zalupaspb}
        
        read -p "Пользователь базы данных (default: postgres): " db_user
        db_user=${db_user:-postgres}
        
        read -sp "Пароль пользователя базы данных: " db_password
        echo
        
        # Создаем базу данных
        echo -e "${YELLOW}Создаем базу данных...${NC}"
        sudo -u postgres psql -c "CREATE DATABASE $db_name;"
        sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $db_name TO $db_user;"
        
        # Обновляем файл .env
        sed -i "s/DB_NAME=.*/DB_NAME=$db_name/" zalupaspb/config/.env
        sed -i "s/DB_USER=.*/DB_USER=$db_user/" zalupaspb/config/.env
        sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=$db_password/" zalupaspb/config/.env
        
        echo -e "${GREEN}База данных создана и настроена${NC}"
    else
        echo -e "${YELLOW}Пропускаем создание базы данных. Убедитесь, что база данных существует и доступна.${NC}"
    fi
else
    echo -e "${YELLOW}Для Windows: Настройте PostgreSQL вручную и обновите файл .env${NC}"
    echo -e "1. Установите PostgreSQL с https://www.postgresql.org/download/windows/"
    echo -e "2. Создайте базу данных 'zalupaspb'"
    echo -e "3. Обновите параметры подключения в файле zalupaspb\\config\\.env"
fi

# Миграции Django
echo -e "${YELLOW}Выполняем миграции Django...${NC}"
if [ "$WINDOWS" = true ]; then
    cd zalupaspb\\web
else
    cd zalupaspb/web
fi
python manage.py migrate

# Создание суперпользователя
echo -e "${YELLOW}Создание суперпользователя Django...${NC}"
read -p "Создать суперпользователя? (y/n): " create_superuser
if [ "$create_superuser" = "y" ]; then
    python manage.py createsuperuser
    echo -e "${GREEN}Суперпользователь создан${NC}"
else
    echo -e "${YELLOW}Пропускаем создание суперпользователя${NC}"
fi

# Сбор статических файлов
echo -e "${YELLOW}Сбор статических файлов...${NC}"
python manage.py collectstatic --noinput

# Настройка Nginx (только для Linux)
if [ "$WINDOWS" = false ]; then
    read -p "Настроить Nginx? (y/n): " setup_nginx
    if [ "$setup_nginx" = "y" ]; then
        echo -e "${YELLOW}Устанавливаем и настраиваем Nginx...${NC}"
        sudo apt-get update
        sudo apt-get install -y nginx
        
        # Создаем конфигурацию для Nginx
        echo -e "${YELLOW}Создаем конфигурацию для Nginx...${NC}"
        read -p "Введите имя домена (без www): " domain_name
        
        sudo bash -c "cat > /etc/nginx/sites-available/zalupaspb << EOL
server {
    listen 80;
    server_name $domain_name www.$domain_name;

    location /static/ {
        alias $(pwd)/staticfiles/;
    }

    location /media/ {
        alias $(pwd)/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection \"upgrade\";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOL"
        
        # Включаем сайт
        sudo ln -s /etc/nginx/sites-available/zalupaspb /etc/nginx/sites-enabled/
        sudo nginx -t && sudo systemctl restart nginx
        
        # Настраиваем SSL с Certbot
        read -p "Настроить SSL с Certbot? (y/n): " setup_ssl
        if [ "$setup_ssl" = "y" ]; then
            echo -e "${YELLOW}Настраиваем SSL с Certbot...${NC}"
            sudo apt-get install -y certbot python3-certbot-nginx
            sudo certbot --nginx -d $domain_name -d www.$domain_name
            echo -e "${GREEN}SSL настроен${NC}"
        fi
        
        echo -e "${GREEN}Nginx настроен${NC}"
    else
        echo -e "${YELLOW}Пропускаем настройку Nginx${NC}"
    fi

    # Настройка Gunicorn и systemd (только для Linux)
    read -p "Настроить Gunicorn и systemd? (y/n): " setup_gunicorn
    if [ "$setup_gunicorn" = "y" ]; then
        echo -e "${YELLOW}Настраиваем Gunicorn и systemd...${NC}"
        
        # Создаем systemd сервис для веб-приложения
        sudo bash -c "cat > /etc/systemd/system/zalupaspb-web.service << EOL
[Unit]
Description=ZalupaSPB Web Service
After=network.target

[Service]
User=$(whoami)
Group=$(id -gn)
WorkingDirectory=$(pwd)
ExecStart=$(which gunicorn) --workers 3 --bind 127.0.0.1:8000 zalupaspb.wsgi:application
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOL"
        
        # Создаем systemd сервис для Discord бота
        sudo bash -c "cat > /etc/systemd/system/zalupaspb-bot.service << EOL
[Unit]
Description=ZalupaSPB Discord Bot
After=network.target

[Service]
User=$(whoami)
Group=$(id -gn)
WorkingDirectory=$(cd ../../bot && pwd)
ExecStart=$(which python) bot.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOL"
        
        # Запускаем и включаем сервисы
        sudo systemctl daemon-reload
        sudo systemctl enable zalupaspb-web.service zalupaspb-bot.service
        sudo systemctl start zalupaspb-web.service
        
        echo -e "${GREEN}Gunicorn и systemd настроены${NC}"
    else
        echo -e "${YELLOW}Пропускаем настройку Gunicorn и systemd${NC}"
    fi
else
    echo -e "${YELLOW}Для Windows: Настройте службы вручную${NC}"
    echo -e "1. Установите и настройте nginx для Windows, если необходимо"
    echo -e "2. Для запуска сервера в продакшн используйте gunicorn или daphne"
    echo -e "3. Для автозапуска используйте Windows Task Scheduler"
fi

# Возвращаемся в корневую директорию проекта
if [ "$WINDOWS" = true ]; then
    cd ..\..
else
    cd ../..
fi

echo -e "${GREEN}Установка ZalupaSPB завершена!${NC}"
echo -e "${YELLOW}Для запуска веб-приложения в режиме разработки:${NC}"
if [ "$WINDOWS" = true ]; then
    echo -e "cd zalupaspb\\web && python manage.py runserver"
    echo -e "${YELLOW}Для запуска Discord бота:${NC}"
    echo -e "cd zalupaspb\\bot && python bot.py"
else
    echo -e "cd zalupaspb/web && python manage.py runserver"
    echo -e "${YELLOW}Для запуска Discord бота:${NC}"
    echo -e "cd zalupaspb/bot && python bot.py"
fi 