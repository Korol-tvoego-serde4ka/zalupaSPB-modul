#!/bin/bash

# Проверка статуса Nginx
echo "==== Проверка статуса Nginx ===="
systemctl status nginx | grep -E 'Active:|PID:'
echo ""

# Проверка конфигурации Nginx
echo "==== Проверка конфигурации Nginx ===="
nginx -t
echo ""

# Проверка прослушиваемых портов
echo "==== Список прослушиваемых портов ===="
ss -tulpn | grep -E ':(80|443|8000|8001)'
echo ""

# Проверка логов Django
echo "==== Последние строки логов Django ===="
echo "--- application.log ---"
tail -n 20 /var/log/zalupaspb/application.log 2>/dev/null || echo "Файл не найден"
echo ""
echo "--- error.log ---"
tail -n 20 /var/log/zalupaspb/error.log 2>/dev/null || echo "Файл не найден"
echo ""

# Проверка системных сервисов для Django
echo "==== Статус сервисов Django ===="
systemctl status zalupaspb.service 2>/dev/null || echo "Сервис не найден"
systemctl status gunicorn.service 2>/dev/null || echo "Сервис не найден"
systemctl status daphne.service 2>/dev/null || echo "Сервис не найден"
echo ""

# Проверка проблем в логах journalctl
echo "==== Ошибки в логах запуска Django (journalctl) ===="
journalctl -u zalupaspb.service -u gunicorn.service -u daphne.service -n 30 --grep='error|critical|fail|exception' 2>/dev/null || echo "Логи не найдены"
echo ""

echo "==== Статус Redis (для channels) ===="
systemctl status redis-server 2>/dev/null || echo "Сервис не найден"
echo ""

echo "==== Проверка доступа к базе данных PostgreSQL ===="
ps aux | grep postgres
echo ""

echo "==== Проверка конфигурационных директорий и прав доступа ===="
ls -la /root/zalupaSPB-modul/zalupaspb/web/ 2>/dev/null || echo "Директория не найдена"
echo ""
ls -la /root/zalupaSPB-modul/zalupaspb/web/staticfiles/ 2>/dev/null || echo "Директория не найдена"
echo ""
ls -la /root/zalupaSPB-modul/zalupaspb/web/media/ 2>/dev/null || echo "Директория не найдена"
echo ""
ls -la /root/zalupaSPB-modul/zalupaspb/web/logs/ 2>/dev/null || echo "Директория не найдена" 