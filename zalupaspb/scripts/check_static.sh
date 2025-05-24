#!/bin/bash

# Скрипт для проверки конфигурации статических файлов.

# Пути к директориям (замените на фактические)
STATIC_ROOT="/path/to/zalupaspb/web/staticfiles"
NGINX_USER="www-data"  # пользователь, под которым работает Nginx

echo "=== Проверка статических файлов ==="

# Проверка существования директории
if [ -d "$STATIC_ROOT" ]; then
    echo "✅ Директория статических файлов существует: $STATIC_ROOT"
else
    echo "❌ Директория статических файлов НЕ существует: $STATIC_ROOT"
    echo "   Решение: выполните collectstatic"
    echo "   cd /path/to/zalupaspb/web"
    echo "   python manage.py collectstatic --noinput"
    exit 1
fi

# Проверка наличия файлов админки
ADMIN_CSS="$STATIC_ROOT/admin/css/base.css"
if [ -f "$ADMIN_CSS" ]; then
    echo "✅ Файлы админки найдены: $ADMIN_CSS"
else
    echo "❌ Файлы админки НЕ найдены: $ADMIN_CSS"
    echo "   Решение: выполните collectstatic и проверьте Django settings"
    exit 1
fi

# Проверка прав доступа
if [ -r "$STATIC_ROOT" ]; then
    echo "✅ Директория статических файлов доступна для чтения"
else
    echo "❌ Директория статических файлов НЕ доступна для чтения"
    echo "   Решение: chmod -R 755 $STATIC_ROOT"
    exit 1
fi

# Проверка прав доступа для Nginx
sudo -u $NGINX_USER test -r "$STATIC_ROOT" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Nginx имеет доступ к директории статических файлов"
else
    echo "❌ Nginx НЕ имеет доступа к директории статических файлов"
    echo "   Решение: chown -R $NGINX_USER:$NGINX_USER $STATIC_ROOT"
    echo "   или: chmod -R o+r $STATIC_ROOT"
    exit 1
fi

# Проверка конфигурации Nginx
NGINX_CONF="/etc/nginx/sites-enabled/dinozavrikgugl.ru.conf"
if [ -f "$NGINX_CONF" ]; then
    STATIC_ALIAS=$(grep -r "alias.*staticfiles" $NGINX_CONF | awk '{print $2}' | tr -d ';')
    if [ -n "$STATIC_ALIAS" ]; then
        echo "✅ Путь к статическим файлам в Nginx: $STATIC_ALIAS"
        
        # Проверка соответствия пути
        if [ "$STATIC_ALIAS" != "$STATIC_ROOT/" ]; then
            echo "⚠️ Внимание: Путь в Nginx ($STATIC_ALIAS) не совпадает с фактическим путем ($STATIC_ROOT/)"
            echo "   Решение: исправьте путь в конфигурации Nginx"
        fi
    else
        echo "❌ Путь к статическим файлам в Nginx не найден"
        echo "   Решение: проверьте конфигурацию Nginx"
    fi
else
    echo "❌ Конфигурационный файл Nginx не найден: $NGINX_CONF"
    echo "   Решение: создайте правильную конфигурацию Nginx"
fi

echo "=== Проверка завершена ===" 