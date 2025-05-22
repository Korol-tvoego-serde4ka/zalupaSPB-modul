const winston = require('winston');
const path = require('path');
const config = require('../config/config');

// Создание директории для логов, если её нет
const fs = require('fs');
if (!fs.existsSync(config.logging.directory)) {
  fs.mkdirSync(config.logging.directory, { recursive: true });
}

// Настройка формата лога
const logFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.errors({ stack: true }),
  winston.format.printf(({ level, message, timestamp, stack }) => {
    return `${timestamp} ${level.toUpperCase()}: ${message} ${stack ? '\n' + stack : ''}`;
  })
);

// Создание логгера
const logger = winston.createLogger({
  level: config.logging.level,
  format: logFormat,
  transports: [
    // Вывод в консоль
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        logFormat
      )
    }),
    // Вывод в файл
    new winston.transports.File({
      filename: path.join(config.logging.directory, 'bot.log'),
      maxsize: 5242880, // 5MB
      maxFiles: 5
    }),
    // Отдельный файл для ошибок
    new winston.transports.File({
      filename: path.join(config.logging.directory, 'error.log'),
      level: 'error',
      maxsize: 5242880, // 5MB
      maxFiles: 5
    })
  ]
});

module.exports = logger; 