#!/usr/bin/env python
import os
import sys
import django

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