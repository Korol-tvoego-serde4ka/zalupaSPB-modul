const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');
const axios = require('axios');
const config = require('../config/config');
const logger = require('../utils/logger');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('link')
    .setDescription('Привязка аккаунта Discord к аккаунту на сайте')
    .addStringOption(option =>
      option.setName('code')
        .setDescription('Код привязки, полученный на сайте')
        .setRequired(true)),
  
  async execute(interaction) {
    await interaction.deferReply({ ephemeral: true });
    
    const code = interaction.options.getString('code');
    const discordId = interaction.user.id;
    const discordUsername = interaction.user.tag;
    
    try {
      // Отправляем запрос к API для привязки аккаунта
      const response = await axios.post(`${config.api.baseUrl}/discord/bot/link`, {
        code,
        discordId,
        discordUsername
      });
      
      if (response.data.success) {
        const userData = response.data.data;
        
        // Успешная привязка
        const successEmbed = new EmbedBuilder()
          .setColor(0x00FF00)
          .setTitle('Аккаунт успешно привязан')
          .setDescription(`Ваш Discord-аккаунт успешно привязан к аккаунту ${userData.username} на сайте.`)
          .addFields(
            { name: 'Роль', value: userData.role, inline: true },
            { name: 'Активный ключ', value: userData.hasActiveKeys ? 'Да' : 'Нет', inline: true }
          )
          .setTimestamp();
        
        await interaction.editReply({ embeds: [successEmbed] });
        
        // Выдаем роль на сервере в зависимости от роли пользователя
        const guild = interaction.guild;
        const member = guild.members.cache.get(discordId);
        
        if (member) {
          try {
            // Удаление всех ролей, связанных с системой
            const rolesToRemove = [
              config.discord.roles.user,
              config.discord.roles.moderator,
              config.discord.roles.admin
            ];
            
            for (const roleId of rolesToRemove) {
              if (roleId && member.roles.cache.has(roleId)) {
                await member.roles.remove(roleId);
              }
            }
            
            // Добавление соответствующей роли
            let roleId;
            
            switch (userData.role) {
              case 'admin':
                roleId = config.discord.roles.admin;
                break;
              case 'moderator':
                roleId = config.discord.roles.moderator;
                break;
              default:
                roleId = config.discord.roles.user;
            }
            
            if (roleId) {
              await member.roles.add(roleId);
              logger.info(`Выдана роль ${userData.role} пользователю ${discordUsername}`);
            }
            
          } catch (error) {
            logger.error(`Ошибка при выдаче роли: ${error.message}`);
          }
        }
        
        // Отправка сообщения в лог-канал
        const logChannel = client.channels.cache.get(config.discord.logChannelId);
        
        if (logChannel) {
          const logEmbed = new EmbedBuilder()
            .setColor(0x00FF00)
            .setTitle('Новая привязка аккаунта')
            .setDescription(`Пользователь <@${discordId}> привязал свой Discord к аккаунту ${userData.username}`)
            .addFields(
              { name: 'Роль', value: userData.role, inline: true },
              { name: 'Discord', value: discordUsername, inline: true }
            )
            .setTimestamp();
          
          await logChannel.send({ embeds: [logEmbed] });
        }
        
      } else {
        // Ошибка при привязке
        const errorEmbed = new EmbedBuilder()
          .setColor(0xFF0000)
          .setTitle('Ошибка при привязке аккаунта')
          .setDescription(response.data.message || 'Произошла неизвестная ошибка')
          .setTimestamp();
        
        await interaction.editReply({ embeds: [errorEmbed] });
      }
    } catch (error) {
      logger.error(`Ошибка при привязке аккаунта: ${error.message}`);
      
      // Формируем сообщение об ошибке
      let errorMessage = 'Произошла ошибка при привязке аккаунта';
      
      if (error.response && error.response.data) {
        errorMessage = error.response.data.message || errorMessage;
      }
      
      const errorEmbed = new EmbedBuilder()
        .setColor(0xFF0000)
        .setTitle('Ошибка')
        .setDescription(errorMessage)
        .setTimestamp();
      
      await interaction.editReply({ embeds: [errorEmbed] });
    }
  }
}; 