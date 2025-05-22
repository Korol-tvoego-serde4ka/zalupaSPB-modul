const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const path = require('path');
const rateLimit = require('express-rate-limit');
const connectDB = require('./config/database');
const config = require('./config/config');
const logger = require('./config/logger');

// Импорт маршрутов
const authRoutes = require('./routes/authRoutes');
const keyRoutes = require('./routes/keyRoutes');
const inviteRoutes = require('./routes/inviteRoutes');
const discordRoutes = require('./routes/discordRoutes');
const adminRoutes = require('./routes/adminRoutes');
const moderatorRoutes = require('./routes/moderatorRoutes');

// Инициализация приложения
const app = express();

// Подключение к базе данных
connectDB();

// Настройка middleware
app.use(helmet()); // Безопасность заголовков
app.use(cors(config.security.cors)); // Настройка CORS
app.use(express.json()); // Парсинг JSON
app.use(express.urlencoded({ extended: true })); // Парсинг URL-encoded

// Логирование запросов в разработке
if (config.app.env !== 'production') {
  app.use(morgan('dev'));
}

// Защита от DDoS и брутфорса
const limiter = rateLimit({
  windowMs: config.security.rateLimiting.windowMs,
  max: config.security.rateLimiting.max,
  message: {
    success: false,
    message: 'Слишком много запросов, пожалуйста, попробуйте позже.'
  }
});

// Применяем ограничение на все маршруты аутентификации
app.use('/api/auth', limiter);

// Маршруты API
app.use('/api/auth', authRoutes);
app.use('/api/keys', keyRoutes);
app.use('/api/invites', inviteRoutes);
app.use('/api/discord', discordRoutes);
app.use('/api/admin', adminRoutes);
app.use('/api/moderator', moderatorRoutes);

// Обслуживание статических файлов в production
if (config.app.env === 'production') {
  app.use(express.static(path.join(__dirname, '../public')));
  
  app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, '../public', 'index.html'));
  });
}

// Обработка ошибок 404
app.use((req, res, next) => {
  res.status(404).json({
    success: false,
    message: 'Маршрут не найден'
  });
});

// Глобальный обработчик ошибок
app.use((err, req, res, next) => {
  logger.error(`Unhandled error: ${err.message}`);
  logger.error(err.stack);
  
  res.status(500).json({
    success: false,
    message: 'Внутренняя ошибка сервера'
  });
});

// Запуск сервера
const PORT = config.app.port;

app.listen(PORT, () => {
  logger.info(`Сервер запущен в режиме ${config.app.env} на порту ${PORT}`);
});

// Обработка необработанных исключений
process.on('uncaughtException', (err) => {
  logger.error('Необработанное исключение:', err);
  process.exit(1);
});

// Обработка необработанных отклонений промисов
process.on('unhandledRejection', (reason, promise) => {
  logger.error('Необработанное отклонение промиса:', reason);
});

module.exports = app; 