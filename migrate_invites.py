#!/usr/bin/env python3
import os
import sys
import django

# Добавляем путь к директории проекта
sys.path.append('/root/zalupaSPB-modul/zalupaspb/web')

# Настраиваем окружение Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zalupaspb.settings')
django.setup()

# Генерация и применение миграций
from django.core.management import call_command

print("Генерация миграций...")
call_command('makemigrations', 'invites', '--name', 'increase_invite_code_length')

print("Применение миграций...")
call_command('migrate', 'invites')

print("Миграция успешно применена!")
print("Поле code в модели Invite теперь имеет размер 14 символов.") 