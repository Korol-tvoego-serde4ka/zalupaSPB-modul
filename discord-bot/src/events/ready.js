const { Events } = require('discord.js');
const logger = require('../utils/logger');

module.exports = {
  name: Events.ClientReady,
  once: true,
  execute(client) {
    logger.info(`Бот успешно запущен и вошел как ${client.user.tag}`);
    
    // Установка статуса бота
    client.user.setActivity('ZalupaSPB', { type: 'WATCHING' });
    
    // Вывод информации о серверах, к которым подключен бот
    const guilds = client.guilds.cache.map(guild => `${guild.name} (${guild.id})`);
    logger.info(`Бот подключен к следующим серверам: ${guilds.join(', ')}`);
  }
}; 