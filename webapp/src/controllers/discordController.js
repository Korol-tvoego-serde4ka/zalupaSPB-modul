const DiscordLink = require('../models/DiscordLink');
const User = require('../models/User');
const Log = require('../models/Log');
const config = require('../config/config');
const logger = require('../config/logger');

// Генерация кода для привязки Discord аккаунта
const generateLinkCode = async (req, res) => {
  try {
    const user = req.user;
    
    // Генерируем новый код связи
    const link = await DiscordLink.generateLink(user._id);
    
    // Логирование
    await Log.logDiscord('generate_link_code', user._id, {}, req);
    
    return res.status(201).json({
      success: true,
      message: 'Код для привязки успешно создан',
      data: {
        code: link.code,
        expiresAt: link.expiresAt
      }
    });
  } catch (error) {
    logger.error(`Ошибка при генерации кода связи: ${error.message}`);
    
    return res.status(500).json({
      success: false,
      message: 'Ошибка при генерации кода для привязки'
    });
  }
};

// Отвязка Discord аккаунта
const unlinkDiscord = async (req, res) => {
  try {
    const user = req.user;
    
    // Проверяем, привязан ли Discord аккаунт
    if (!user.discordId) {
      return res.status(400).json({
        success: false,
        message: 'Discord аккаунт не привязан'
      });
    }
    
    // Сохраняем текущий Discord ID для лога
    const oldDiscordId = user.discordId;
    
    // Отвязываем аккаунт
    user.discordId = undefined;
    user.discordUsername = undefined;
    await user.save();
    
    // Логирование
    await Log.logDiscord('unlink', user._id, { oldDiscordId }, req);
    
    return res.status(200).json({
      success: true,
      message: 'Discord аккаунт успешно отвязан'
    });
  } catch (error) {
    logger.error(`Ошибка при отвязке Discord аккаунта: ${error.message}`);
    
    return res.status(500).json({
      success: false,
      message: 'Ошибка при отвязке Discord аккаунта'
    });
  }
};

// Проверка статуса привязки Discord аккаунта
const checkLinkStatus = async (req, res) => {
  try {
    const user = req.user;
    
    return res.status(200).json({
      success: true,
      data: {
        linked: !!user.discordId,
        discordId: user.discordId,
        discordUsername: user.discordUsername
      }
    });
  } catch (error) {
    logger.error(`Ошибка при проверке статуса привязки: ${error.message}`);
    
    return res.status(500).json({
      success: false,
      message: 'Ошибка при проверке статуса привязки'
    });
  }
};

// API для Discord бота - привязка аккаунта по коду
const linkByCode = async (req, res) => {
  try {
    const { code, discordId, discordUsername } = req.body;
    
    if (!code || !discordId || !discordUsername) {
      return res.status(400).json({
        success: false,
        message: 'Все поля обязательны'
      });
    }
    
    // Проверяем, что Discord ID еще не привязан к другому аккаунту
    const existingUser = await User.findOne({ discordId });
    
    if (existingUser) {
      return res.status(400).json({
        success: false,
        message: 'Этот Discord аккаунт уже привязан к другому пользователю'
      });
    }
    
    // Находим и используем код связи
    const link = await DiscordLink.findActiveByCode(code);
    
    if (!link) {
      return res.status(404).json({
        success: false,
        message: 'Недействительный или истекший код связи'
      });
    }
    
    // Используем код и обновляем данные
    await link.use(discordId, discordUsername);
    
    // Обновляем пользователя
    const user = await User.findByIdAndUpdate(
      link.userId,
      {
        discordId,
        discordUsername
      },
      { new: true }
    );
    
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'Пользователь не найден'
      });
    }
    
    // Логирование
    await Log.logDiscord('link', user._id, { discordId, discordUsername });
    
    return res.status(200).json({
      success: true,
      message: 'Discord аккаунт успешно привязан',
      data: {
        userId: user._id,
        username: user.username,
        role: user.role,
        hasActiveKeys: user.activeKeys.length > 0
      }
    });
  } catch (error) {
    logger.error(`Ошибка при привязке по коду: ${error.message}`);
    
    if (error.message === 'Код уже использован или истек' || 
        error.message === 'Срок действия кода истек') {
      return res.status(400).json({
        success: false,
        message: error.message
      });
    }
    
    return res.status(500).json({
      success: false,
      message: 'Ошибка при привязке Discord аккаунта'
    });
  }
};

// API для Discord бота - получение информации о пользователе
const getUserByDiscordId = async (req, res) => {
  try {
    const { discordId } = req.params;
    
    if (!discordId) {
      return res.status(400).json({
        success: false,
        message: 'Discord ID обязателен'
      });
    }
    
    // Находим пользователя
    const user = await User.findOne({ discordId })
      .select('username role activeKeys isBanned')
      .populate('activeKeys')
      .lean();
    
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'Пользователь не найден'
      });
    }
    
    // Проверяем активные ключи
    const hasActiveKey = user.role !== 'user' || user.activeKeys.some(key => 
      key.status === 'used' && (!key.expiresAt || new Date() < key.expiresAt)
    );
    
    return res.status(200).json({
      success: true,
      data: {
        userId: user._id,
        username: user.username,
        role: user.role,
        isBanned: user.isBanned,
        hasActiveKey
      }
    });
  } catch (error) {
    logger.error(`Ошибка при получении пользователя по Discord ID: ${error.message}`);
    
    return res.status(500).json({
      success: false,
      message: 'Ошибка при получении информации о пользователе'
    });
  }
};

module.exports = {
  generateLinkCode,
  unlinkDiscord,
  checkLinkStatus,
  linkByCode,
  getUserByDiscordId
}; 