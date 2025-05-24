#!/usr/bin/env python
import os
import sys
import django

# Устанавливаем переменную окружения
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zalupaspb.settings')

# Запускаем Django
django.setup()

# Импортируем модель LogEntry
from django.contrib.admin.models import LogEntry

# Удаляем все записи из журнала действий
count = LogEntry.objects.all().delete()[0]
print(f"Удалено {count} записей из журнала действий администратора") 