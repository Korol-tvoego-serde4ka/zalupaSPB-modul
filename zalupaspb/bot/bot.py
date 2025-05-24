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
from api_client import APIClient

# Создаем директорию для логов, если она не существует
log_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(log_dir, "bot.log")

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,  # Устанавливаем уровень DEBUG для более подробных логов
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('discord_bot')
logger.info(f"Запуск бота. Лог файл: {log_file}")

# Устанавливаем уровень логирования для библиотек
logging.getLogger('discord').setLevel(logging.INFO)
logging.getLogger('requests').setLevel(logging.DEBUG)
logging.getLogger('urllib3').setLevel(logging.INFO)

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

# Инициализируем API клиент
api_client = APIClient()

@bot.event
async def on_ready():
    """Обработчик события готовности бота"""
    logger.info(f'Бот {bot.user} запущен')
    
    # Синхронизируем команды приложения
    try:
        # Синхронизируем только с конкретным сервером для предотвращения дублирования
        guild = discord.Object(id=GUILD_ID)
        bot.tree.clear_commands(guild=None)  # Очищаем глобальные команды
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
        
        logger.info("Команды приложения синхронизированы только для сервера")
    except Exception as e:
        logger.error(f"Ошибка синхронизации команд: {e}", exc_info=True)


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


@bot.tree.command(name="code", description="Привязать Discord-аккаунт к аккаунту на сайте")
@app_commands.describe(code="Код привязки, полученный на сайте")
async def code_command(interaction: discord.Interaction, code: str):
    """Команда для привязки аккаунта через код с сайта"""
    try:
        logger.info(f"Пользователь {interaction.user.id} ({interaction.user.name}) пытается привязать аккаунт с кодом: {code}")
        
        # Проверяем, не привязан ли уже аккаунт
        user_data = api_client.get_user_by_discord_id(str(interaction.user.id))
        logger.info(f"Результат проверки привязки: {user_data}")
        
        if user_data and not 'error' in user_data:
            await interaction.response.send_message("Ваш Discord аккаунт уже привязан к аккаунту на сайте.", ephemeral=True)
            logger.info(f"Discord аккаунт {interaction.user.id} уже привязан")
            return
        
        # Формируем данные для привязки
        discord_username = f"{interaction.user.name}#{interaction.user.discriminator}" if interaction.user.discriminator != '0' else interaction.user.name
        discord_avatar = str(interaction.user.avatar.url) if interaction.user.avatar else None
        
        logger.info(f"Отправляем запрос на привязку с данными: code={code}, discord_id={interaction.user.id}, discord_username={discord_username}")
        
        # Отправляем запрос на привязку
        result = api_client.bind_discord(
            code,
            str(interaction.user.id),
            discord_username,
            discord_avatar
        )
        
        logger.info(f"Результат привязки: {result}")
        
        if 'error' in result:
            await interaction.response.send_message(f"Ошибка привязки аккаунта: {result.get('error')}", ephemeral=True)
            logger.error(f"Ошибка привязки для {interaction.user.id}: {result.get('error')}")
            return
        
        await interaction.response.send_message("Аккаунт успешно привязан!", ephemeral=True)
        await log_message(f"Пользователь {interaction.user.mention} привязал Discord-аккаунт к аккаунту на сайте")
        logger.info(f"Аккаунт {interaction.user.id} успешно привязан")
    except Exception as e:
        logger.error(f"Исключение при выполнении команды /code: {e}", exc_info=True)
        try:
            await interaction.response.send_message(f"Произошла ошибка при выполнении команды: {str(e)}", ephemeral=True)
        except:
            # Если не удалось отправить ответ через response, пробуем через followup
            try:
                await interaction.followup.send(f"Произошла ошибка при выполнении команды: {str(e)}", ephemeral=True)
            except Exception as followup_error:
                logger.error(f"Не удалось отправить сообщение об ошибке: {followup_error}")
                pass


@bot.tree.command(name="redeem", description="Активировать ключ")
@app_commands.describe(key="Ключ для активации")
async def redeem_command(interaction: discord.Interaction, key: str):
    """Команда для активации ключа"""
    # Проверяем наличие привязанного аккаунта
    user_id = str(interaction.user.id)
    
    # Получаем пользователя по discord_id
    user_data = api_client.get_user_by_discord_id(user_id)
    
    if 'error' in user_data or not user_data:
        await interaction.response.send_message("Ваш Discord аккаунт не привязан к аккаунту на сайте. Используйте команду /code для получения кода привязки.", ephemeral=True)
        return
    
    # Отправляем запрос на API для активации ключа
    try:
        result = api_client.activate_key(key, user_data.get('id'))
        
        if 'error' in result:
            await interaction.response.send_message(f"Ошибка активации ключа: {result.get('error')}", ephemeral=True)
            return
            
        await interaction.response.send_message(f"Ключ успешно активирован!", ephemeral=True)
        await log_message(f"Пользователь {interaction.user.mention} активировал ключ {key}")
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
    
    # Создаем ключ через API
    result = api_client.create_key(key_type, duration_days)
    
    if 'error' in result:
        await interaction.response.send_message(f"Ошибка генерации ключа: {result.get('error')}", ephemeral=True)
        return
        
    key_code = result.get('key_code', 'Неизвестный ключ')
    
    await interaction.response.send_message(f"Ключ успешно сгенерирован: `{key_code}`\nТип: {key_type}\nСрок действия: {duration_days} дней", ephemeral=True)
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
    
    # Получаем пользователя по discord_id
    user_data = api_client.get_user_by_discord_id(str(user.id))
    
    if 'error' in user_data or not user_data:
        await interaction.response.send_message(f"Пользователь {user.mention} не найден в системе.", ephemeral=True)
        return
    
    # Блокируем пользователя через API
    result = api_client.ban_user(user_data.get('id'), reason)
    
    if 'error' in result:
        await interaction.response.send_message(f"Ошибка блокировки пользователя: {result.get('error')}", ephemeral=True)
        return
    
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
    
    # Получаем пользователя по discord_id
    user_data = api_client.get_user_by_discord_id(str(user.id))
    
    if 'error' in user_data or not user_data:
        await interaction.response.send_message(f"Пользователь {user.mention} не найден в системе.", ephemeral=True)
        return
    
    # Разблокируем пользователя через API
    result = api_client.unban_user(user_data.get('id'))
    
    if 'error' in result:
        await interaction.response.send_message(f"Ошибка разблокировки пользователя: {result.get('error')}", ephemeral=True)
        return
    
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
    
    # Получаем пользователя по discord_id
    user_data = api_client.get_user_by_discord_id(str(user.id))
    
    if 'error' in user_data or not user_data:
        await interaction.response.send_message(f"Пользователь {user.mention} не найден в системе.", ephemeral=True)
        return
    
    # Получаем статистику пользователя
    stats = api_client.get_user_stats(user_data.get('id'))
    
    if 'error' in stats:
        await interaction.response.send_message(f"Ошибка получения статистики: {stats.get('error')}", ephemeral=True)
        return
    
    # Создаем embed для отображения статистики
    embed = discord.Embed(title=f"Статистика пользователя {user.display_name}", color=0x00ff00)
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name="Discord ID", value=user.id, inline=False)
    embed.add_field(name="Роль", value=stats.get('role', 'Неизвестно'), inline=True)
    embed.add_field(name="Дата регистрации", value=stats.get('date_joined', 'Неизвестно'), inline=True)
    embed.add_field(name="Активные ключи", value=stats.get('active_keys_count', 0), inline=True)
    embed.add_field(name="Доступно инвайтов", value=stats.get('available_invites', 0), inline=True)
    
    if stats.get('is_banned'):
        embed.add_field(name="Статус", value="Заблокирован", inline=True)
    
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


# После определения slash-команды добавляем обычную команду

@bot.command(name="code", description="Привязать Discord-аккаунт к аккаунту на сайте")
async def code_prefix_command(ctx, code: str = None):
    """Обычная команда для привязки аккаунта через код с сайта"""
    if not code:
        await ctx.send("Укажите код привязки, полученный на сайте. Пример: `!code ABC123`")
        return
    
    try:
        logger.info(f"Пользователь {ctx.author.id} ({ctx.author.name}) пытается привязать аккаунт с кодом: {code} (префиксная команда)")
        
        # Проверяем, не привязан ли уже аккаунт
        user_data = api_client.get_user_by_discord_id(str(ctx.author.id))
        logger.info(f"Результат проверки привязки: {user_data}")
        
        if user_data and not 'error' in user_data:
            await ctx.send("Ваш Discord аккаунт уже привязан к аккаунту на сайте.")
            logger.info(f"Discord аккаунт {ctx.author.id} уже привязан")
            return
        
        # Формируем данные для привязки
        discord_username = f"{ctx.author.name}#{ctx.author.discriminator}" if ctx.author.discriminator != '0' else ctx.author.name
        discord_avatar = str(ctx.author.avatar.url) if ctx.author.avatar else None
        
        logger.info(f"Отправляем запрос на привязку с данными: code={code}, discord_id={ctx.author.id}, discord_username={discord_username}")
        
        # Отправляем запрос на привязку
        result = api_client.bind_discord(
            code,
            str(ctx.author.id),
            discord_username,
            discord_avatar
        )
        
        logger.info(f"Результат привязки: {result}")
        
        if 'error' in result:
            await ctx.send(f"Ошибка привязки аккаунта: {result.get('error')}")
            logger.error(f"Ошибка привязки для {ctx.author.id}: {result.get('error')}")
            return
        
        await ctx.send("Аккаунт успешно привязан!")
        await log_message(f"Пользователь {ctx.author.mention} привязал Discord-аккаунт к аккаунту на сайте")
        logger.info(f"Аккаунт {ctx.author.id} успешно привязан")
    except Exception as e:
        logger.error(f"Исключение при выполнении команды !code: {e}", exc_info=True)
        await ctx.send(f"Произошла ошибка при выполнении команды: {str(e)}")


# После события on_ready добавим команду для принудительной синхронизации

@bot.command(name="sync", description="Синхронизация слэш-команд (только для администраторов)")
@commands.is_owner()  # Только владелец бота может использовать
async def sync_command(ctx, sync_type: str = "guild"):
    """Синхронизирует слэш-команды с Discord
    
    sync_type: 
        - guild: синхронизация только для текущего сервера (по умолчанию)
        - global: синхронизация глобально
        - clear: очистка всех команд
    """
    try:
        logger.info(f"Попытка синхронизации команд от пользователя {ctx.author.name} с типом {sync_type}")
        
        if sync_type == "guild":
            # Синхронизация только для текущего сервера
            guild = discord.Object(id=GUILD_ID)
            bot.tree.clear_commands(guild=guild)
            bot.tree.copy_global_to(guild=guild)
            await bot.tree.sync(guild=guild)
            await ctx.send("Команды синхронизированы для этого сервера!")
        elif sync_type == "global":
            # Глобальная синхронизация
            bot.tree.clear_commands(guild=None)
            await bot.tree.sync()
            await ctx.send("Команды синхронизированы глобально!")
        elif sync_type == "clear":
            # Очистка всех команд
            bot.tree.clear_commands(guild=None)
            bot.tree.clear_commands(guild=discord.Object(id=GUILD_ID))
            await bot.tree.sync()
            await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
            await ctx.send("Все команды очищены!")
        else:
            await ctx.send("Неизвестный тип синхронизации. Используйте: guild, global или clear")
            return
        
        logger.info(f"Команды успешно синхронизированы с типом {sync_type}")
    except Exception as e:
        logger.error(f"Ошибка при синхронизации команд: {e}", exc_info=True)
        await ctx.send(f"Ошибка при синхронизации команд: {str(e)}")


# Добавляем в конце файла, перед запуском бота

@bot.command(name="api_check", description="Проверка настроек API (только для администраторов)")
@commands.is_owner()  # Только владелец бота может использовать
async def api_check_command(ctx):
    """Проверяет настройки API и выполняет тестовый запрос"""
    try:
        base_url = api_client.base_url
        
        # Формируем сообщение со всеми настройками API
        message = f"**Настройки API**\n"
        message += f"База API: `{base_url}`\n"
        message += f"Имеется токен: `{'Да' if api_client.token else 'Нет'}`\n"
        message += f"Имеется refresh токен: `{'Да' if api_client.refresh_token else 'Нет'}`\n"
        
        # Проверяем доступность API
        logger.info(f"Проверка доступности {base_url}")
        
        try:
            response = requests.get(base_url, timeout=5)
            message += f"\nСтатус API: `{response.status_code}`\n"
            message += f"Ответ: ```{response.text[:200]}...```\n" if len(response.text) > 200 else f"Ответ: ```{response.text}```\n"
        except Exception as e:
            message += f"\nОшибка при проверке API: `{str(e)}`\n"
        
        # Отправляем сообщение с информацией
        await ctx.send(message)
        logger.info(f"Проверка API выполнена для пользователя {ctx.author.name}")
    except Exception as e:
        logger.error(f"Ошибка при выполнении команды api_check: {e}", exc_info=True)
        await ctx.send(f"Ошибка при проверке API: {str(e)}")


# Запуск бота
if __name__ == "__main__":
    try:
        bot.run(BOT_TOKEN)
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")
        sys.exit(1) 