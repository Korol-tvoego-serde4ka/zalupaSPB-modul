const winston = require('winston');
const path = require('path');

// Настройка формата лога
const logFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.errors({ stack: true }),
  winston.format.printf(({ level, message, timestamp, stack }) => {
    return `${timestamp} ${level.toUpperCase()}: ${message} ${stack ? '\n' + stack : ''}`;
  })
);

// Настройка транспортов логирования
const transports = [
  // Консольный вывод
  new winston.transports.Console({
    level: process.env.NODE_ENV === 'production' ? 'info' : 'debug',
    format: winston.format.combine(
      winston.format.colorize(),
      logFormat
    )
  }),
  // Файл с основными логами
  new winston.transports.File({
    filename: path.join('logs', 'app.log'),
    level: 'info',
    format: logFormat,
    maxsize: 5242880, // 5MB
    maxFiles: 5
  }),
  // Файл только с ошибками
  new winston.transports.File({
    filename: path.join('logs', 'error.log'),
    level: 'error',
    format: logFormat,
    maxsize: 5242880, // 5MB
    maxFiles: 5
  })
];

// Создание логгера
const logger = winston.createLogger({
  level: process.env.NODE_ENV === 'production' ? 'info' : 'debug',
  format: logFormat,
  transports,
  exitOnError: false
});

// Перехватываем неперехваченные исключения
logger.exceptions.handle(
  new winston.transports.File({
    filename: path.join('logs', 'exceptions.log'),
    format: logFormat,
    maxsize: 5242880, // 5MB
    maxFiles: 5
  })
);

// Перехватываем необработанные отклонения промисов
process.on('unhandledRejection', (ex) => {
  throw ex;
});

module.exports = logger; 