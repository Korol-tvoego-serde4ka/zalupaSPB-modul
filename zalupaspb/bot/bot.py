import os
import sys
import logging
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
import yaml
from dotenv import load_dotenv
import random
import string
import requests
import json
from datetime import datetime, timedelta

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('discord_bot')

# Загружаем переменные окружения
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', '.env'))

# Загружаем конфигурацию
try:
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'config.yaml'), 'r') as f:
        config = yaml.safe_load(f)
except Exception as e:
    logger.error(f"Ошибка загрузки конфигурации: {e}")
    sys.exit(1)

# Получаем токен бота из переменных окружения
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
if not BOT_TOKEN:
    logger.error("Токен Discord бота не найден в переменных окружения")
    sys.exit(1)

# Настройки API
API_URL = os.getenv('API_URL', 'http://localhost:8000/api')

# Настройки Discord
GUILD_ID = int(os.getenv('DISCORD_GUILD_ID', config.get('discord', {}).get('guild_id', 0)))
ADMIN_ROLE_ID = int(os.getenv('DISCORD_ADMIN_ROLE_ID', config.get('discord', {}).get('roles', {}).get('admin', 0)))
MODERATOR_ROLE_ID = int(os.getenv('DISCORD_MODERATOR_ROLE_ID', config.get('discord', {}).get('roles', {}).get('moderator', 0)))
SUPPORT_ROLE_ID = int(os.getenv('DISCORD_SUPPORT_ROLE_ID', config.get('discord', {}).get('roles', {}).get('support', 0)))
USER_ROLE_ID = int(os.getenv('DISCORD_USER_ROLE_ID', config.get('discord', {}).get('roles', {}).get('user', 0)))
LOG_CHANNEL_ID = int(os.getenv('DISCORD_LOG_CHANNEL_ID', config.get('discord', {}).get('channels', {}).get('log', 0)))

# Создаем интенты и бота
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Кеш для временных кодов привязки
binding_codes = {}


@bot.event
async def on_ready():
    """Обработчик события готовности бота"""
    logger.info(f'Бот {bot.user} запущен')
    
    # Синхронизируем команды приложения
    try:
        await bot.tree.sync()
        logger.info("Команды приложения синхронизированы")
    except Exception as e:
        logger.error(f"Ошибка синхронизации команд: {e}")


@bot.event
async def on_member_update(before, after):
    """Обработчик изменения пользователя на сервере"""
    # Проверяем, что это наш сервер
    if after.guild.id != GUILD_ID:
        return
    
    # Проверяем, изменились ли роли
    if before.roles == after.roles:
        return
    
    # Получаем роли
    roles_before = set([role.id for role in before.roles])
    roles_after = set([role.id for role in after.roles])
    
    # Проверяем добавление/удаление ролей администратора, модератора и т.д.
    important_roles = {
        ADMIN_ROLE_ID: 'admin',
        MODERATOR_ROLE_ID: 'moderator',
        SUPPORT_ROLE_ID: 'support',
        USER_ROLE_ID: 'user'
    }
    
    for role_id, role_name in important_roles.items():
        if role_id in roles_after and role_id not in roles_before:
            # Роль добавлена
            await log_message(f"Пользователю {after.mention} добавлена роль {role_name}")
        elif role_id in roles_before and role_id not in roles_after:
            # Роль удалена
            await log_message(f"У пользователя {after.mention} удалена роль {role_name}")


@bot.tree.command(name="code", description="Получить код для привязки Discord-аккаунта к аккаунту на сайте")
async def code_command(interaction: discord.Interaction):
    """Команда для получения кода привязки"""
    # Генерируем код привязки
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    # Сохраняем код в кеше на 15 минут
    binding_codes[interaction.user.id] = {
        'code': code,
        'expires_at': datetime.now() + timedelta(minutes=15)
    }
    
    # Отправляем код в личные сообщения
    try:
        await interaction.user.send(f"Ваш код для привязки аккаунта: **{code}**\nКод действителен в течение 15 минут.")
        await interaction.response.send_message("Код для привязки отправлен вам в личные сообщения.", ephemeral=True)
        await log_message(f"Пользователь {interaction.user.mention} запросил код привязки")
    except discord.Forbidden:
        await interaction.response.send_message("Не удалось отправить вам личное сообщение. Пожалуйста, разрешите получение сообщений от участников сервера.", ephemeral=True)


@bot.tree.command(name="redeem", description="Активировать ключ")
@app_commands.describe(key="Ключ для активации")
async def redeem_command(interaction: discord.Interaction, key: str):
    """Команда для активации ключа"""
    # Проверяем наличие привязанного аккаунта
    user_id = str(interaction.user.id)
    
    # Отправляем запрос на API для активации ключа
    try:
        # Здесь должна быть реализация запроса к API
        # Для примера просто выводим успех
        await interaction.response.send_message(f"Ключ успешно активирован!", ephemeral=True)
        await log_message(f"Пользователь {interaction.user.mention} активировал ключ")
    except Exception as e:
        await interaction.response.send_message(f"Ошибка активации ключа: {str(e)}", ephemeral=True)


@bot.tree.command(name="generate_key", description="Сгенерировать новый ключ (только для админов и модераторов)")
@app_commands.describe(
    key_type="Тип ключа (standard, premium, lifetime)",
    duration_days="Срок действия в днях (для стандартных и премиум ключей)"
)
@app_commands.choices(key_type=[
    app_commands.Choice(name="Стандартный (30 дней)", value="standard"),
    app_commands.Choice(name="Премиум (90 дней)", value="premium"),
    app_commands.Choice(name="Пожизненный", value="lifetime")
])
async def generate_key_command(
    interaction: discord.Interaction, 
    key_type: str = "standard",
    duration_days: int = None
):
    """Команда для генерации ключа"""
    # Проверяем права доступа
    if not has_permission(interaction.user, [ADMIN_ROLE_ID, MODERATOR_ROLE_ID]):
        await interaction.response.send_message("У вас нет прав для выполнения этой команды.", ephemeral=True)
        return
    
    # Устанавливаем срок действия по умолчанию в зависимости от типа ключа
    if duration_days is None:
        if key_type == "standard":
            duration_days = 30
        elif key_type == "premium":
            duration_days = 90
        else:  # lifetime
            duration_days = 0  # Бессрочно
    
    # Здесь должна быть реализация запроса к API для генерации ключа
    # Для примера просто выводим фейковый ключ
    fake_key = f"{key_type.upper()}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
    
    await interaction.response.send_message(f"Ключ успешно сгенерирован: `{fake_key}`\nТип: {key_type}\nСрок действия: {duration_days} дней", ephemeral=True)
    await log_message(f"Пользователь {interaction.user.mention} сгенерировал ключ типа {key_type}")


@bot.tree.command(name="ban", description="Заблокировать пользователя (только для админов, модераторов и поддержки)")
@app_commands.describe(
    user="Пользователь для блокировки",
    reason="Причина блокировки"
)
async def ban_command(interaction: discord.Interaction, user: discord.Member, reason: str = "Нарушение правил"):
    """Команда для блокировки пользователя"""
    # Проверяем права доступа
    if not has_permission(interaction.user, [ADMIN_ROLE_ID, MODERATOR_ROLE_ID, SUPPORT_ROLE_ID]):
        await interaction.response.send_message("У вас нет прав для выполнения этой команды.", ephemeral=True)
        return
    
    # Проверяем, что не блокируем админа будучи не админом
    if has_permission(user, [ADMIN_ROLE_ID]) and not has_permission(interaction.user, [ADMIN_ROLE_ID]):
        await interaction.response.send_message("Вы не можете заблокировать администратора.", ephemeral=True)
        return
    
    # Здесь должна быть реализация запроса к API для блокировки пользователя
    # Для примера просто выводим сообщение
    await interaction.response.send_message(f"Пользователь {user.mention} заблокирован. Причина: {reason}", ephemeral=True)
    await log_message(f"Пользователь {interaction.user.mention} заблокировал {user.mention}. Причина: {reason}")


@bot.tree.command(name="unban", description="Разблокировать пользователя (только для админов и модераторов)")
@app_commands.describe(
    user="Пользователь для разблокировки"
)
async def unban_command(interaction: discord.Interaction, user: discord.Member):
    """Команда для разблокировки пользователя"""
    # Проверяем права доступа
    if not has_permission(interaction.user, [ADMIN_ROLE_ID, MODERATOR_ROLE_ID]):
        await interaction.response.send_message("У вас нет прав для выполнения этой команды.", ephemeral=True)
        return
    
    # Здесь должна быть реализация запроса к API для разблокировки пользователя
    # Для примера просто выводим сообщение
    await interaction.response.send_message(f"Пользователь {user.mention} разблокирован.", ephemeral=True)
    await log_message(f"Пользователь {interaction.user.mention} разблокировал {user.mention}")


@bot.tree.command(name="stats", description="Показать статистику пользователя")
@app_commands.describe(
    user="Пользователь для просмотра статистики (не указывайте для просмотра своей статистики)"
)
async def stats_command(interaction: discord.Interaction, user: discord.Member = None):
    """Команда для просмотра статистики пользователя"""
    # Если пользователь не указан, используем автора команды
    if user is None:
        user = interaction.user
    
    # Если запрашиваем статистику другого пользователя, проверяем права доступа
    if user.id != interaction.user.id and not has_permission(interaction.user, [ADMIN_ROLE_ID, MODERATOR_ROLE_ID, SUPPORT_ROLE_ID]):
        await interaction.response.send_message("У вас нет прав для просмотра статистики других пользователей.", ephemeral=True)
        return
    
    # Здесь должна быть реализация запроса к API для получения статистики пользователя
    # Для примера просто выводим фейковую статистику
    embed = discord.Embed(title=f"Статистика пользователя {user.display_name}", color=0x00ff00)
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name="Discord ID", value=user.id, inline=False)
    embed.add_field(name="Роль", value="Пользователь", inline=True)
    embed.add_field(name="Дата регистрации", value=user.created_at.strftime("%d.%m.%Y"), inline=True)
    embed.add_field(name="Активные ключи", value="1", inline=True)
    embed.add_field(name="Доступно инвайтов", value="2", inline=True)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)


# Вспомогательные функции
async def log_message(message):
    """Отправка сообщения в лог-канал"""
    if LOG_CHANNEL_ID:
        channel = bot.get_channel(LOG_CHANNEL_ID)
        if channel:
            try:
                await channel.send(f"[{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}] {message}")
            except Exception as e:
                logger.error(f"Ошибка отправки сообщения в лог-канал: {e}")


def has_permission(member, role_ids):
    """Проверка наличия у пользователя одной из ролей"""
    return any(role.id in role_ids for role in member.roles)


# Запуск бота
if __name__ == "__main__":
    try:
        bot.run(BOT_TOKEN)
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")
        sys.exit(1) 