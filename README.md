# ZalupaSPB - Система управления доступом

ZalupaSPB - это комплексная система, состоящая из веб-приложения и Discord-бота с интеграцией MongoDB, предназначенная для управления доступом пользователей через систему ключей и инвайтов.

## Содержание

- [Системные требования](#системные-требования)
- [Компоненты системы](#компоненты-системы)
- [Предварительная настройка](#предварительная-настройка)
  - [Настройка Discord бота](#настройка-discord-бота)
  - [Настройка переменных окружения](#настройка-переменных-окружения)
- [Установка и запуск](#установка-и-запуск)
  - [Клонирование репозитория](#клонирование-репозитория)
  - [Настройка переменных окружения](#настройка-переменных-окружения)
  - [Запуск с помощью Docker Compose](#запуск-с-помощью-docker-compose)
  - [Запуск без Docker](#запуск-без-docker)
- [Проверка работоспособности](#проверка-работоспособности)
- [Управление системой](#управление-системой)
- [Структура проекта](#структура-проекта)
- [Устранение неполадок](#устранение-неполадок)

## Системные требования

- **Docker** и **Docker Compose** (рекомендуется для простой установки)
- **Node.js** (v14 или новее) - если запускаете без Docker
- **MongoDB** (v4.4 или новее) - если запускаете без Docker
- **npm** или **yarn** - если запускаете без Docker
- **Созданный Discord Bot** с необходимыми разрешениями

## Компоненты системы

Система состоит из трех основных компонентов:

1. **Web-приложение** - серверная часть API для управления пользователями, ключами и инвайтами.
2. **Discord-бот** - интеграция с Discord для привязки аккаунтов и проверки статуса.
3. **MongoDB** - база данных для хранения всех данных системы.

## Предварительная настройка

### Настройка Discord бота

1. Перейдите на [Discord Developer Portal](https://discord.com/developers/applications)
2. Создайте новое приложение, нажав кнопку "New Application"
3. Перейдите в раздел "Bot" и нажмите "Add Bot"
4. Настройте бота:
   - Включите опции "Presence Intent", "Server Members Intent" и "Message Content Intent" 
   - В разделе "Bot Permissions" выберите необходимые разрешения (рекомендуется: Manage Roles, Send Messages, Read Messages, Embed Links)
5. Сохраните токен бота ("Token") - он понадобится для настройки переменных окружения
6. Перейдите в раздел "OAuth2" -> "URL Generator":
   - В разделе "Scopes" выберите "bot" и "applications.commands"
   - В разделе "Bot Permissions" выберите те же разрешения, что указаны в шаге 4
   - Скопируйте сгенерированную ссылку и используйте её для добавления бота на ваш сервер

### Настройка переменных окружения

Создайте файл `.env` в корневой директории проекта со следующими переменными:

```
# MongoDB
MONGO_USERNAME=admin
MONGO_PASSWORD=your_secure_password

# Web Application
WEB_PORT=3000
JWT_SECRET=your_secure_jwt_secret

# Discord Integration
DISCORD_CLIENT_ID=your_discord_client_id
DISCORD_CLIENT_SECRET=your_discord_client_secret
DISCORD_REDIRECT_URI=http://your-domain.com/api/auth/discord/callback
DISCORD_BOT_TOKEN=your_discord_bot_token
DISCORD_GUILD_ID=your_discord_server_id
DISCORD_LOG_CHANNEL_ID=your_discord_log_channel_id
DISCORD_USER_ROLE_ID=your_discord_user_role_id
DISCORD_MOD_ROLE_ID=your_discord_mod_role_id
DISCORD_ADMIN_ROLE_ID=your_discord_admin_role_id
```

## Установка и запуск

### Клонирование репозитория

```bash
https://github.com/Korol-tvoego-serde4ka/zalupaSPB-modul.git
cd zalupaspb-modul
```

### Настройка переменных окружения

1. Скопируйте пример файла переменных окружения:
   ```bash
   cp .env.example .env
   ```
2. Отредактируйте файл `.env`, заполнив его согласно инструкции в разделе "Настройка переменных окружения"

### Запуск с помощью Docker Compose

1. Убедитесь, что Docker и Docker Compose установлены и запущены
2. Соберите и запустите контейнеры:
   ```bash
   docker-compose up -d
   ```
3. Проверьте, что все контейнеры запустились:
   ```bash
   docker-compose ps
   ```

Все компоненты системы будут запущены автоматически:
- MongoDB доступен на порту 27017
- Web-приложение доступно на порту, указанном в переменной WEB_PORT (по умолчанию 3000)
- Discord-бот будет запущен и подключен к Discord

### Запуск без Docker

#### 1. База данных MongoDB

Установите и запустите MongoDB:

```bash
# Пример для Ubuntu
sudo apt update
sudo apt install -y mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

#### 2. Web-приложение

```bash
cd webapp
npm install
npm start
```

Для разработки можно использовать:
```bash
npm run dev
```

#### 3. Discord-бот

```bash
cd discord-bot
npm install
node src/index.js
```

## Проверка работоспособности

### Web-приложение

Проверьте доступность веб-приложения, открыв в браузере:
```
http://localhost:3000/api
```

Вы должны получить сообщение о 404 ошибке (маршрут не найден), что означает, что сервер запущен и отвечает.

### Discord-бот

Убедитесь, что бот онлайн на вашем Discord-сервере. Попробуйте выполнить команду:
```
/status
```

## Управление системой

### Создание администратора

Для создания первого администратора системы необходимо:

1. Создать инвайт-код вручную в базе данных MongoDB:
   ```javascript
   use zalupaspb
   db.invites.insertOne({
     code: "ADMIN",
     createdBy: ObjectId("000000000000000000000000"),
     status: "active",
     role: "admin",
     expiresAt: new Date(Date.now() + 86400000),
     createdAt: new Date(),
     updatedAt: new Date()
   })
   ```

2. Использовать этот инвайт-код при регистрации первого пользователя через веб-интерфейс или API.

### Основные функции системы

- **Регистрация пользователей** - только по инвайт-кодам
- **Инвайт-система** - пользователи могут приглашать новых участников
- **Ключи доступа** - временный или постоянный доступ к функциям
- **Интеграция с Discord** - синхронизация ролей и статусов
- **Административная панель** - управление пользователями и мониторинг

## Структура проекта

```
zalupaspb-modul/
├── docker-compose.yml    # Конфигурация Docker-контейнеров
├── webapp/               # Web-приложение
│   ├── Dockerfile        # Docker конфигурация для веб-приложения
│   ├── package.json      # Зависимости Node.js
│   └── src/              # Исходный код веб-приложения
│       ├── app.js        # Основной файл приложения
│       ├── config/       # Конфигурационные файлы
│       ├── controllers/  # Контроллеры API
│       ├── middlewares/  # Middleware функции
│       ├── models/       # Mongoose модели данных
│       └── routes/       # API маршруты
│
└── discord-bot/          # Discord бот
    ├── src/              # Исходный код Discord бота
    │   ├── index.js      # Основной файл бота
    │   ├── commands/     # Команды Discord бота
    │   ├── events/       # Обработчики событий Discord
    │   ├── config/       # Конфигурация бота
    │   └── utils/        # Утилиты
```

## Устранение неполадок

### Проблемы с подключением к MongoDB

Если веб-приложение или Discord бот не могут подключиться к MongoDB:

1. Проверьте правильность учетных данных в файле `.env`
2. Проверьте, запущен ли контейнер с MongoDB:
   ```bash
   docker-compose ps mongodb
   ```
3. Проверьте логи MongoDB:
   ```bash
   docker-compose logs mongodb
   ```

### Проблемы с Discord ботом

Если Discord бот не подключается:

1. Проверьте токен бота в файле `.env`
2. Убедитесь, что включены необходимые интенты в панели управления Discord Developer Portal
3. Проверьте логи бота:
   ```bash
   docker-compose logs discord-bot
   ```

### Перезапуск системы

Для полного перезапуска системы:

```bash
docker-compose down
docker-compose up -d
```

Для перезапуска отдельных компонентов:

```bash
docker-compose restart webapp
docker-compose restart discord-bot
```

## Лицензия

Этот проект предоставляется "как есть" без каких-либо гарантий. 
