const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');
const axios = require('axios');
const config = require('../config/config');
const logger = require('../utils/logger');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('status')
    .setDescription('Проверка статуса вашего аккаунта'),
  
  async execute(interaction) {
    await interaction.deferReply({ ephemeral: true });
    
    const discordId = interaction.user.id;
    
    try {
      // Проверяем статус пользователя через API
      const response = await axios.get(`${config.api.baseUrl}/discord/bot/user/${discordId}`);
      
      if (response.data.success) {
        const userData = response.data.data;
        
        // Создаем embed для отображения информации о пользователе
        const statusEmbed = new EmbedBuilder()
          .setColor(userData.hasActiveKey ? 0x00FF00 : 0xFFAA00)
          .setTitle('Статус аккаунта')
          .setDescription(`Информация о вашем аккаунте на сайте ZalupaSPB`)
          .addFields(
            { name: 'Имя пользователя', value: userData.username, inline: true },
            { name: 'Роль', value: userData.role, inline: true },
            { name: 'Активный ключ', value: userData.hasActiveKey ? 'Да' : 'Нет', inline: true },
            { name: 'Статус аккаунта', value: userData.isBanned ? '⛔ Заблокирован' : '✅ Активен', inline: true }
          )
          .setTimestamp();
        
        // Если аккаунт заблокирован, добавляем причину
        if (userData.isBanned) {
          statusEmbed.addFields(
            { name: 'Причина блокировки', value: userData.banReason || 'Не указана' }
          );
        }
        
        await interaction.editReply({ embeds: [statusEmbed] });
        
      } else {
        const errorEmbed = new EmbedBuilder()
          .setColor(0xFF0000)
          .setTitle('Ошибка')
          .setDescription(response.data.message || 'Произошла ошибка при проверке статуса')
          .setTimestamp();
        
        await interaction.editReply({ embeds: [errorEmbed] });
      }
    } catch (error) {
      logger.error(`Ошибка при проверке статуса: ${error.message}`);
      
      // Проверяем, связан ли ошибка с тем, что пользователь не найден
      if (error.response && error.response.status === 404) {
        const notFoundEmbed = new EmbedBuilder()
          .setColor(0xFF0000)
          .setTitle('Аккаунт не найден')
          .setDescription('Ваш Discord-аккаунт не привязан к аккаунту на сайте. Используйте команду `/link` для привязки.')
          .setTimestamp();
        
        await interaction.editReply({ embeds: [notFoundEmbed] });
        return;
      }
      
      // Общая ошибка
      const errorEmbed = new EmbedBuilder()
        .setColor(0xFF0000)
        .setTitle('Ошибка')
        .setDescription('Произошла ошибка при проверке статуса аккаунта.')
        .setTimestamp();
      
      await interaction.editReply({ embeds: [errorEmbed] });
    }
  }
}; 