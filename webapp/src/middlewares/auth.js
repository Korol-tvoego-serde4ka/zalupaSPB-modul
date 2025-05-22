const jwt = require('jsonwebtoken');
const config = require('../config/config');
const User = require('../models/User');
const logger = require('../config/logger');

// Middleware для проверки наличия JWT токена и его верификации
const authenticate = async (req, res, next) => {
  try {
    // Получаем токен из заголовка авторизации
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ 
        success: false, 
        message: 'Требуется авторизация' 
      });
    }
    
    const token = authHeader.split(' ')[1];
    
    // Верифицируем JWT токен
    const decoded = jwt.verify(token, config.jwt.secret);
    
    // Ищем пользователя в базе данных
    const user = await User.findById(decoded.id);
    
    if (!user) {
      return res.status(401).json({ 
        success: false, 
        message: 'Пользователь не найден' 
      });
    }
    
    if (user.isBanned) {
      return res.status(403).json({ 
        success: false, 
        message: 'Аккаунт заблокирован',
        banReason: user.banReason
      });
    }
    
    // Добавляем пользователя к объекту запроса
    req.user = user;
    
    // Переходим к следующему middleware
    next();
  } catch (error) {
    if (error.name === 'JsonWebTokenError') {
      return res.status(401).json({ 
        success: false, 
        message: 'Недействительный токен' 
      });
    } else if (error.name === 'TokenExpiredError') {
      return res.status(401).json({ 
        success: false, 
        message: 'Срок действия токена истек' 
      });
    }
    
    logger.error(`Ошибка аутентификации: ${error.message}`);
    
    return res.status(500).json({ 
      success: false, 
      message: 'Внутренняя ошибка сервера' 
    });
  }
};

// Middleware для проверки роли пользователя
const authorize = (roles = []) => {
  // Преобразуем в массив, если передана строка
  if (typeof roles === 'string') {
    roles = [roles];
  }
  
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ 
        success: false, 
        message: 'Требуется авторизация' 
      });
    }
    
    if (roles.length && !roles.includes(req.user.role)) {
      return res.status(403).json({ 
        success: false, 
        message: 'Недостаточно прав для выполнения этого действия' 
      });
    }
    
    next();
  };
};

// Middleware для проверки, что пользователь имеет активный ключ
const requireActiveKey = async (req, res, next) => {
  try {
    if (!req.user) {
      return res.status(401).json({ 
        success: false, 
        message: 'Требуется авторизация' 
      });
    }
    
    // Проверяем, есть ли у пользователя активные ключи
    const user = await User.findById(req.user._id).populate('activeKeys');
    
    const hasValidKey = user.activeKeys.some(key => {
      return key.status === 'used' && (!key.expiresAt || new Date() < key.expiresAt);
    });
    
    if (!hasValidKey && user.role === 'user') {
      return res.status(403).json({ 
        success: false, 
        message: 'Для доступа требуется активный ключ' 
      });
    }
    
    next();
  } catch (error) {
    logger.error(`Ошибка проверки ключа: ${error.message}`);
    
    return res.status(500).json({ 
      success: false, 
      message: 'Внутренняя ошибка сервера' 
    });
  }
};

module.exports = {
  authenticate,
  authorize,
  requireActiveKey
}; 