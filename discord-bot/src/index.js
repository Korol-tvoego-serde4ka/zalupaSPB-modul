require('dotenv').config();
const { Client, GatewayIntentBits, Collection, Events } = require('discord.js');
const fs = require('fs');
const path = require('path');
const mongoose = require('mongoose');
const logger = require('./utils/logger');
const config = require('./config/config');

// Создание нового клиента Discord
const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.GuildMembers
  ]
});

// Коллекция команд
client.commands = new Collection();

// Загрузка команд
const commandsPath = path.join(__dirname, 'commands');
const commandFiles = fs.readdirSync(commandsPath).filter(file => file.endsWith('.js'));

for (const file of commandFiles) {
  const filePath = path.join(commandsPath, file);
  const command = require(filePath);
  
  // Добавляем команду в коллекцию
  if ('data' in command && 'execute' in command) {
    client.commands.set(command.data.name, command);
    logger.info(`Загружена команда: ${command.data.name}`);
  } else {
    logger.warn(`Команда по пути ${filePath} не содержит необходимых свойств "data" или "execute"`);
  }
}

// Загрузка обработчиков событий
const eventsPath = path.join(__dirname, 'events');
const eventFiles = fs.readdirSync(eventsPath).filter(file => file.endsWith('.js'));

for (const file of eventFiles) {
  const filePath = path.join(eventsPath, file);
  const event = require(filePath);
  
  if (event.once) {
    client.once(event.name, (...args) => event.execute(...args, client));
  } else {
    client.on(event.name, (...args) => event.execute(...args, client));
  }
  
  logger.info(`Загружен обработчик события: ${event.name}`);
}

// Подключение к MongoDB
mongoose.connect(config.database.uri, config.database.options)
  .then(() => {
    logger.info('Бот успешно подключился к MongoDB');
  })
  .catch((err) => {
    logger.error(`Ошибка подключения к MongoDB: ${err.message}`);
    process.exit(1);
  });

// Обработка ошибок и исключений
process.on('unhandledRejection', (error) => {
  logger.error(`Необработанное отклонение промиса: ${error.message}`);
  logger.error(error.stack);
});

process.on('uncaughtException', (error) => {
  logger.error(`Необработанное исключение: ${error.message}`);
  logger.error(error.stack);
  process.exit(1);
});

// Запуск бота
client.login(config.discord.token)
  .catch((error) => {
    logger.error(`Ошибка при входе в Discord: ${error.message}`);
    process.exit(1);
  }); 