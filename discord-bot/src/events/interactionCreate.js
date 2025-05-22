const { Events } = require('discord.js');
const logger = require('../utils/logger');

module.exports = {
  name: Events.InteractionCreate,
  async execute(interaction, client) {
    // Обработка команд Slash
    if (interaction.isChatInputCommand()) {
      const command = client.commands.get(interaction.commandName);
      
      if (!command) {
        logger.error(`Команда ${interaction.commandName} не найдена`);
        return;
      }
      
      try {
        logger.info(`Пользователь ${interaction.user.tag} использовал команду ${interaction.commandName}`);
        await command.execute(interaction, client);
      } catch (error) {
        logger.error(`Ошибка при выполнении команды ${interaction.commandName}`);
        logger.error(error.stack);
        
        // Отправка уведомления об ошибке пользователю
        const content = {
          content: 'Произошла ошибка при выполнении команды',
          ephemeral: true
        };
        
        if (interaction.replied || interaction.deferred) {
          await interaction.followUp(content);
        } else {
          await interaction.reply(content);
        }
      }
    }
    // Обработка кнопок
    else if (interaction.isButton()) {
      const buttonId = interaction.customId;
      logger.info(`Пользователь ${interaction.user.tag} нажал кнопку ${buttonId}`);
      
      // Здесь можно добавить обработку кнопок
    }
  }
}; 