#!/usr/bin/env python
import os
import sys
import django

# Добавляем путь к директории проекта в sys.path
sys.path.append('/root/zalupaSPB-modul/zalupaspb/web')

# Устанавливаем переменную окружения для настроек
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zalupaspb.settings')

# Запускаем Django
django.setup()

# Импортируем модель LogEntry
from django.contrib.admin.models import LogEntry

# Удаляем все записи из журнала действий
count = LogEntry.objects.all().delete()[0]
print(f"Удалено {count} записей из журнала действий администратора") 