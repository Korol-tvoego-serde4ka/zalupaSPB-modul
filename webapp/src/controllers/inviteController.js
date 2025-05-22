const Invite = require('../models/Invite');
const User = require('../models/User');
const Log = require('../models/Log');
const logger = require('../config/logger');

// Создание нового инвайт-кода
const createInvite = async (req, res) => {
  try {
    const { role = 'user', expiresIn } = req.body;
    const user = req.user;
    
    // Проверяем, что пользователь может создавать инвайты с указанной ролью
    if (role !== 'user' && user.role === 'moderator') {
      return res.status(403).json({
        success: false,
        message: 'У вас нет прав на создание инвайтов с этой ролью'
      });
    }
    
    // Создаем инвайт
    let expiresAt = null;
    if (expiresIn) {
      expiresAt = new Date(Date.now() + expiresIn * 1000);
    }
    
    const invite = await Invite.generateInvite(user._id, {
      role,
      expiresAt
    });
    
    // Логирование
    await Log.logInvite('create', user._id, invite._id, {
      role,
      expiresAt
    }, req);
    
    return res.status(201).json({
      success: true,
      message: 'Инвайт-код успешно создан',
      data: { invite }
    });
  } catch (error) {
    logger.error(`Ошибка при создании инвайт-кода: ${error.message}`);
    
    if (error.message === 'У вас закончились доступные приглашения') {
      return res.status(400).json({
        success: false,
        message: error.message
      });
    }
    
    return res.status(500).json({
      success: false,
      message: 'Ошибка при создании инвайт-кода'
    });
  }
};

// Получение списка созданных инвайтов пользователя
const getMyInvites = async (req, res) => {
  try {
    const user = req.user;
    
    // Проверяем количество доступных инвайтов
    user.resetInvitesIfNeeded();
    await user.save();
    
    // Получаем инвайты, созданные пользователем
    const invites = await Invite.find({ createdBy: user._id })
      .sort({ createdAt: -1 })
      .populate('usedBy', 'username')
      .lean();
    
    return res.status(200).json({
      success: true,
      data: {
        invites,
        invitesLeft: user.invitesLeft
      }
    });
  } catch (error) {
    logger.error(`Ошибка при получении инвайтов: ${error.message}`);
    
    return res.status(500).json({
      success: false,
      message: 'Ошибка при получении списка инвайтов'
    });
  }
};

// Получение всех инвайтов (admin/moderator)
const getAllInvites = async (req, res) => {
  try {
    const { page = 1, limit = 20, status, role, userId } = req.query;
    
    // Создаем условие для фильтрации
    const filter = {};
    
    if (status) filter.status = status;
    if (role) filter.role = role;
    if (userId) filter.createdBy = userId;
    
    // Получаем инвайты с пагинацией
    const invites = await Invite.find(filter)
      .populate('createdBy', 'username role')
      .populate('usedBy', 'username')
      .sort({ createdAt: -1 })
      .skip((page - 1) * limit)
      .limit(parseInt(limit))
      .lean();
    
    // Получаем общее количество инвайтов
    const total = await Invite.countDocuments(filter);
    
    return res.status(200).json({
      success: true,
      data: {
        invites,
        pagination: {
          total,
          page: parseInt(page),
          limit: parseInt(limit),
          pages: Math.ceil(total / limit)
        }
      }
    });
  } catch (error) {
    logger.error(`Ошибка при получении всех инвайтов: ${error.message}`);
    
    return res.status(500).json({
      success: false,
      message: 'Ошибка при получении всех инвайтов'
    });
  }
};

// Отзыв инвайт-кода
const revokeInvite = async (req, res) => {
  try {
    const { inviteId } = req.params;
    const user = req.user;
    
    // Находим инвайт
    const invite = await Invite.findById(inviteId);
    
    if (!invite) {
      return res.status(404).json({
        success: false,
        message: 'Инвайт не найден'
      });
    }
    
    // Проверяем права на отзыв
    if (invite.createdBy.toString() !== user._id.toString() && user.role === 'user') {
      return res.status(403).json({
        success: false,
        message: 'У вас нет прав на отзыв этого инвайта'
      });
    }
    
    if (invite.status !== 'active') {
      return res.status(400).json({
        success: false,
        message: 'Инвайт уже использован или отозван'
      });
    }
    
    // Отзываем инвайт
    invite.status = 'revoked';
    await invite.save();
    
    // Если пользователь отозвал свой инвайт, возвращаем ему приглашение
    if (invite.createdBy.toString() === user._id.toString() && user.role !== 'admin') {
      user.invitesLeft += 1;
      await user.save();
    }
    
    // Логирование
    await Log.logInvite('revoke', user._id, invite._id, {}, req);
    
    return res.status(200).json({
      success: true,
      message: 'Инвайт успешно отозван'
    });
  } catch (error) {
    logger.error(`Ошибка при отзыве инвайта: ${error.message}`);
    
    return res.status(500).json({
      success: false,
      message: 'Ошибка при отзыве инвайта'
    });
  }
};

// Проверка валидности инвайт-кода
const checkInviteCode = async (req, res) => {
  try {
    const { code } = req.body;
    
    if (!code) {
      return res.status(400).json({
        success: false,
        message: 'Код приглашения обязателен'
      });
    }
    
    // Находим активный инвайт по коду
    const invite = await Invite.findActiveByCode(code);
    
    if (!invite) {
      return res.status(404).json({
        success: false,
        message: 'Недействительный или истекший код приглашения'
      });
    }
    
    return res.status(200).json({
      success: true,
      data: {
        valid: true,
        invite: {
          id: invite._id,
          code: invite.code,
          role: invite.role,
          expiresAt: invite.expiresAt
        }
      }
    });
  } catch (error) {
    logger.error(`Ошибка при проверке инвайт-кода: ${error.message}`);
    
    return res.status(500).json({
      success: false,
      message: 'Ошибка при проверке инвайт-кода'
    });
  }
};

// Получение пользователей, приглашенных текущим пользователем
const getInvitedUsers = async (req, res) => {
  try {
    const user = req.user;
    
    // Получаем детали пользователя с инвайтами
    const userDoc = await User.findById(user._id)
      .populate({
        path: 'invitedUsers',
        select: 'username email role createdAt',
        populate: {
          path: 'activeKeys',
          select: 'status activatedAt expiresAt'
        }
      })
      .select('invitedUsers');
    
    return res.status(200).json({
      success: true,
      data: {
        users: userDoc.invitedUsers
      }
    });
  } catch (error) {
    logger.error(`Ошибка при получении приглашенных пользователей: ${error.message}`);
    
    return res.status(500).json({
      success: false,
      message: 'Ошибка при получении приглашенных пользователей'
    });
  }
};

module.exports = {
  createInvite,
  getMyInvites,
  getAllInvites,
  revokeInvite,
  checkInviteCode,
  getInvitedUsers
}; 