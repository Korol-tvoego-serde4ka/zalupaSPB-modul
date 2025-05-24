#!/bin/bash

# Скрипт для настройки SSL-сертификатов с помощью Certbot

# Проверяем, запущен ли скрипт с правами root
if [ "$EUID" -ne 0 ]; then
  echo "Этот скрипт должен быть запущен с правами root"
  exit 1
fi

# Определяем домен
DOMAIN="dinozavrikgugl.ru"
EMAIL="admin@dinozavrikgugl.ru"  # Замените на свой email для уведомлений

# Устанавливаем certbot, если он еще не установлен
if ! [ -x "$(command -v certbot)" ]; then
  echo "Certbot не установлен. Устанавливаем..."
  apt-get update
  apt-get install -y certbot python3-certbot-nginx
fi

# Получаем SSL-сертификат для основного домена и www поддомена
echo "Получаем SSL-сертификат для $DOMAIN и www.$DOMAIN..."
certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email $EMAIL --redirect

# Настройка автоматического обновления сертификатов
echo "Настройка автоматического обновления сертификатов..."
(crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet --deploy-hook 'systemctl reload nginx'") | crontab -

echo "Установка SSL-сертификатов завершена."
echo "Настроено перенаправление с HTTP на HTTPS."
echo "Настроено автоматическое обновление сертификатов каждый день в 3:00."

# Проверяем конфигурацию Nginx
echo "Проверка конфигурации Nginx..."
nginx -t

if [ $? -eq 0 ]; then
  echo "Конфигурация Nginx корректна. Перезапускаем Nginx..."
  systemctl restart nginx
else
  echo "Ошибка в конфигурации Nginx. Пожалуйста, проверьте и исправьте ошибки вручную."
  exit 1
fi

echo "SSL настройка завершена успешно!" 