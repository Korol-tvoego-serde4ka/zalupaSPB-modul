module.exports = {
  // Настройки Discord
  discord: {
    token: process.env.DISCORD_BOT_TOKEN,
    clientId: process.env.DISCORD_CLIENT_ID,
    guildId: process.env.DISCORD_GUILD_ID,
    // Каналы
    logChannelId: process.env.DISCORD_LOG_CHANNEL_ID,
    // Роли
    roles: {
      user: process.env.DISCORD_USER_ROLE_ID,
      moderator: process.env.DISCORD_MOD_ROLE_ID,
      admin: process.env.DISCORD_ADMIN_ROLE_ID
    }
  },
  
  // Настройки базы данных
  database: {
    uri: process.env.MONGO_URI || 'mongodb://localhost:27017/zalupaspb',
    options: {
      useNewUrlParser: true,
      useUnifiedTopology: true
    }
  },
  
  // Настройки API
  api: {
    baseUrl: process.env.API_BASE_URL || 'http://webapp:3000/api'
  },
  
  // Настройки логирования
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    directory: process.env.LOG_DIR || './logs'
  }
}; 