const Key = require('../models/Key');
const User = require('../models/User');
const Log = require('../models/Log');
const logger = require('../config/logger');

// Генерация нового ключа
const generateKey = async (req, res) => {
  try {
    const { duration, type = 'default', metadata = {} } = req.body;
    const user = req.user;
    
    // Проверяем права пользователя на создание ключей
    if (user.role === 'user') {
      return res.status(403).json({
        success: false,
        message: 'У вас нет прав на генерацию ключей'
      });
    }
    
    // Создаем новый ключ
    const key = await Key.generateKey(user._id, {
      duration,
      type,
      metadata
    });
    
    // Логирование
    await Log.logKey('generate', user._id, key._id, {
      duration,
      type,
      metadata
    }, req);
    
    return res.status(201).json({
      success: true,
      message: 'Ключ успешно создан',
      data: { key }
    });
  } catch (error) {
    logger.error(`Ошибка при генерации ключа: ${error.message}`);
    
    return res.status(500).json({
      success: false,
      message: 'Ошибка при генерации ключа'
    });
  }
};

// Получение всех ключей пользователя
const getMyKeys = async (req, res) => {
  try {
    const user = req.user;
    
    // Находим активные ключи пользователя и обновляем их статус
    const activeKeys = await User.findById(user._id)
      .populate('activeKeys')
      .select('activeKeys')
      .lean();
    
    // Обновляем статус каждого ключа
    const updatedKeys = await Promise.all(
      activeKeys.activeKeys.map(async (key) => {
        const keyDoc = await Key.findById(key._id);
        
        if (keyDoc) {
          await keyDoc.updateStatus();
          return keyDoc;
        }
        
        return null;
      })
    );
    
    // Фильтруем null значения
    const keys = updatedKeys.filter(key => key !== null);
    
    return res.status(200).json({
      success: true,
      data: { keys }
    });
  } catch (error) {
    logger.error(`Ошибка при получении ключей: ${error.message}`);
    
    return res.status(500).json({
      success: false,
      message: 'Ошибка при получении ключей'
    });
  }
};

// Получение всех ключей (админское действие)
const getAllKeys = async (req, res) => {
  try {
    const { page = 1, limit = 20, status, type, userId } = req.query;
    
    // Создаем условие для фильтрации
    const filter = {};
    
    if (status) filter.status = status;
    if (type) filter.type = type;
    if (userId) filter.createdBy = userId;
    
    // Получаем ключи с пагинацией
    const keys = await Key.find(filter)
      .populate('createdBy', 'username role')
      .populate('usedBy', 'username')
      .sort({ createdAt: -1 })
      .skip((page - 1) * limit)
      .limit(parseInt(limit))
      .lean();
    
    // Получаем общее количество ключей
    const total = await Key.countDocuments(filter);
    
    return res.status(200).json({
      success: true,
      data: {
        keys,
        pagination: {
          total,
          page: parseInt(page),
          limit: parseInt(limit),
          pages: Math.ceil(total / limit)
        }
      }
    });
  } catch (error) {
    logger.error(`Ошибка при получении всех ключей: ${error.message}`);
    
    return res.status(500).json({
      success: false,
      message: 'Ошибка при получении всех ключей'
    });
  }
};

// Активация ключа
const activateKey = async (req, res) => {
  try {
    const { keyCode } = req.body;
    const user = req.user;
    
    if (!keyCode) {
      return res.status(400).json({
        success: false,
        message: 'Код ключа обязателен'
      });
    }
    
    // Находим активный ключ по коду
    const key = await Key.findActiveKeyByCode(keyCode);
    
    if (!key) {
      return res.status(404).json({
        success: false,
        message: 'Ключ не найден или уже использован'
      });
    }
    
    // Активируем ключ
    await key.activate(user._id);
    
    // Добавляем ключ к активным ключам пользователя
    await User.findByIdAndUpdate(user._id, {
      $push: { activeKeys: key._id }
    });
    
    // Логирование
    await Log.logKey('activate', user._id, key._id, {}, req);
    
    return res.status(200).json({
      success: true,
      message: 'Ключ успешно активирован',
      data: { key }
    });
  } catch (error) {
    logger.error(`Ошибка при активации ключа: ${error.message}`);
    
    if (error.message === 'Ключ уже использован или истек') {
      return res.status(400).json({
        success: false,
        message: error.message
      });
    }
    
    return res.status(500).json({
      success: false,
      message: 'Ошибка при активации ключа'
    });
  }
};

// Отзыв ключа (админское действие)
const revokeKey = async (req, res) => {
  try {
    const { keyId } = req.params;
    const user = req.user;
    
    // Находим ключ
    const key = await Key.findById(keyId);
    
    if (!key) {
      return res.status(404).json({
        success: false,
        message: 'Ключ не найден'
      });
    }
    
    // Отзываем ключ
    key.status = 'revoked';
    await key.save();
    
    // Если ключ был привязан к пользователю, удаляем его из активных
    if (key.usedBy) {
      await User.findByIdAndUpdate(key.usedBy, {
        $pull: { activeKeys: key._id }
      });
    }
    
    // Логирование
    await Log.logKey('revoke', user._id, key._id, {}, req);
    
    return res.status(200).json({
      success: true,
      message: 'Ключ успешно отозван'
    });
  } catch (error) {
    logger.error(`Ошибка при отзыве ключа: ${error.message}`);
    
    return res.status(500).json({
      success: false,
      message: 'Ошибка при отзыве ключа'
    });
  }
};

// Получение ключа по ID
const getKeyById = async (req, res) => {
  try {
    const { keyId } = req.params;
    
    // Находим ключ
    const key = await Key.findById(keyId)
      .populate('createdBy', 'username role')
      .populate('usedBy', 'username')
      .lean();
    
    if (!key) {
      return res.status(404).json({
        success: false,
        message: 'Ключ не найден'
      });
    }
    
    return res.status(200).json({
      success: true,
      data: { key }
    });
  } catch (error) {
    logger.error(`Ошибка при получении ключа: ${error.message}`);
    
    return res.status(500).json({
      success: false,
      message: 'Ошибка при получении ключа'
    });
  }
};

// Проверка статуса ключей пользователя
const checkKeyStatus = async (req, res) => {
  try {
    const user = req.user;
    
    // Находим активные ключи пользователя и обновляем их статус
    const userDoc = await User.findById(user._id).populate('activeKeys');
    
    // Обновляем статус каждого ключа
    await Promise.all(
      userDoc.activeKeys.map(async (key) => {
        await key.updateStatus();
      })
    );
    
    // Фильтруем ключи, которые всё ещё активны
    const activeKeys = userDoc.activeKeys.filter(key => key.status === 'used' && !key.isExpired());
    
    return res.status(200).json({
      success: true,
      data: {
        hasValidKey: activeKeys.length > 0,
        keys: activeKeys
      }
    });
  } catch (error) {
    logger.error(`Ошибка при проверке статуса ключей: ${error.message}`);
    
    return res.status(500).json({
      success: false,
      message: 'Ошибка при проверке статуса ключей'
    });
  }
};

module.exports = {
  generateKey,
  getMyKeys,
  getAllKeys,
  activateKey,
  revokeKey,
  getKeyById,
  checkKeyStatus
}; 