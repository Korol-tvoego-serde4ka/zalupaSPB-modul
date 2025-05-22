const dotenv = require('dotenv');
const path = require('path');

// Загрузка переменных окружения из файла .env
dotenv.config();

// Базовая конфигурация приложения
const config = {
  // Информация о приложении
  app: {
    name: 'ZalupaSPB',
    version: process.env.npm_package_version || '1.0.0',
    env: process.env.NODE_ENV || 'development',
    port: process.env.PORT || 3000,
    baseUrl: process.env.BASE_URL || 'http://localhost:3000'
  },
  
  // JWT настройки
  jwt: {
    secret: process.env.JWT_SECRET || 'very-secure-jwt-secret-for-zalupaspb',
    accessExpiresIn: process.env.JWT_ACCESS_EXPIRES_IN || '15m',
    refreshExpiresIn: process.env.JWT_REFRESH_EXPIRES_IN || '7d'
  },
  
  // Настройки безопасности
  security: {
    bcryptSaltRounds: 10,
    rateLimiting: {
      windowMs: 15 * 60 * 1000, // 15 минут
      max: 100 // максимум 100 запросов за 15 минут
    },
    cors: {
      origin: process.env.CORS_ORIGIN || '*',
      methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
      allowedHeaders: ['Content-Type', 'Authorization']
    }
  },
  
  // Настройки MongoDB
  db: {
    uri: process.env.MONGO_URI || 'mongodb://localhost:27017/zalupaspb'
  },
  
  // Настройки для Discord интеграции
  discord: {
    clientId: process.env.DISCORD_CLIENT_ID,
    clientSecret: process.env.DISCORD_CLIENT_SECRET,
    redirectUri: process.env.DISCORD_REDIRECT_URI || 'http://localhost:3000/api/auth/discord/callback',
    botToken: process.env.DISCORD_BOT_TOKEN,
    guildId: process.env.DISCORD_GUILD_ID,
    roles: {
      user: process.env.DISCORD_USER_ROLE_ID,
      moderator: process.env.DISCORD_MOD_ROLE_ID,
      admin: process.env.DISCORD_ADMIN_ROLE_ID
    },
    logChannelId: process.env.DISCORD_LOG_CHANNEL_ID
  },
  
  // Настройки для логирования
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    directory: process.env.LOG_DIR || path.join(process.cwd(), 'logs')
  },
  
  // Настройки по умолчанию для пользователей
  defaults: {
    invites: {
      user: 2,
      moderator: 10,
      admin: Infinity
    },
    expirations: {
      inviteCode: 7 * 24 * 60 * 60 * 1000, // 7 дней в миллисекундах
      discordLink: 15 * 60 * 1000, // 15 минут в миллисекундах
      key: 30 * 24 * 60 * 60 // 30 дней в секундах
    }
  }
};

module.exports = config; 