const mongoose = require('mongoose');
const logger = require('./logger');

// Функция для подключения к базе данных MongoDB
const connectDB = async () => {
  try {
    const mongoURI = process.env.MONGO_URI || 'mongodb://localhost:27017/zalupaspb';
    
    const options = {
      useNewUrlParser: true,
      useUnifiedTopology: true,
      serverSelectionTimeoutMS: 5000
    };
    
    // Подключение к MongoDB
    await mongoose.connect(mongoURI, options);
    
    logger.info('MongoDB успешно подключена');
    
    // Обработка событий подключения
    mongoose.connection.on('error', (err) => {
      logger.error(`Ошибка соединения с MongoDB: ${err.message}`);
    });
    
    mongoose.connection.on('disconnected', () => {
      logger.warn('MongoDB отключена');
    });
    
    // Обработка сигналов завершения для корректного закрытия соединения
    process.on('SIGINT', async () => {
      await mongoose.connection.close();
      logger.info('Соединение с MongoDB закрыто');
      process.exit(0);
    });
    
  } catch (error) {
    logger.error(`Ошибка подключения к MongoDB: ${error.message}`);
    process.exit(1);
  }
};

module.exports = connectDB; 