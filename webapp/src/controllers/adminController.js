const User = require('../models/User');
const Key = require('../models/Key');
const Log = require('../models/Log');
const logger = require('../config/logger');

// Получение списка всех пользователей
const getAllUsers = async (req, res) => {
  try {
    const { page = 1, limit = 20, role, search } = req.query;
    
    // Создаем условие для фильтрации
    const filter = {};
    
    if (role) filter.role = role;
    if (search) {
      filter.$or = [
        { username: new RegExp(search, 'i') },
        { email: new RegExp(search, 'i') }
      ];
    }
    
    // Получаем пользователей с пагинацией
    const users = await User.find(filter)
      .select('-password')
      .sort({ createdAt: -1 })
      .skip((page - 1) * limit)
      .limit(parseInt(limit))
      .lean();
    
    // Получаем общее количество пользователей
    const total = await User.countDocuments(filter);
    
    return res.status(200).json({
      success: true,
      data: {
        users,
        pagination: {
          total,
          page: parseInt(page),
          limit: parseInt(limit),
          pages: Math.ceil(total / limit)
        }
      }
    });
  } catch (error) {
    logger.error(`Ошибка при получении пользователей: ${error.message}`);
    
    return res.status(500).json({
      success: false,
      message: 'Ошибка при получении списка пользователей'
    });
  }
};

// Получение информации о пользователе по ID
const getUserById = async (req, res) => {
  try {
    const { userId } = req.params;
    
    // Находим пользователя
    const user = await User.findById(userId)
      .select('-password')
      .populate('invitedBy', 'username')
      .populate('activeKeys')
      .lean();
    
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'Пользователь не найден'
      });
    }
    
    // Получаем дополнительную статистику
    const invitedUsersCount = await User.countDocuments({ invitedBy: userId });
    const createdKeysCount = await Key.countDocuments({ createdBy: userId });
    
    return res.status(200).json({
      success: true,
      data: {
        user,
        stats: {
          invitedUsersCount,
          createdKeysCount
        }
      }
    });
  } catch (error) {
    logger.error(`Ошибка при получении пользователя: ${error.message}`);
    
    return res.status(500).json({
      success: false,
      message: 'Ошибка при получении информации о пользователе'
    });
  }
};

// Обновление роли пользователя
const updateUserRole = async (req, res) => {
  try {
    const { userId } = req.params;
    const { role } = req.body;
    const adminUser = req.user;
    
    if (!role || !['user', 'moderator', 'admin'].includes(role)) {
      return res.status(400).json({
        success: false,
        message: 'Некорректная роль'
      });
    }
    
    // Находим пользователя
    const user = await User.findById(userId);
    
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'Пользователь не найден'
      });
    }
    
    // Проверяем права на изменение
    if (adminUser.role !== 'admin' && (user.role === 'admin' || role === 'admin')) {
      return res.status(403).json({
        success: false,
        message: 'У вас нет прав на это действие'
      });
    }
    
    // Сохраняем старую роль для лога
    const oldRole = user.role;
    
    // Обновляем роль
    user.role = role;
    
    // Обновляем количество доступных инвайтов в зависимости от новой роли
    if (role === 'admin') {
      user.invitesLeft = Number.MAX_SAFE_INTEGER;
    } else if (role === 'moderator' && oldRole !== 'moderator') {
      user.invitesLeft = Math.max(user.invitesLeft, 10);
    }
    
    await user.save();
    
    // Логирование
    await Log.logAdmin('update_role', adminUser._id, user._id, 'User', {
      oldRole,
      newRole: role
    }, req);
    
    return res.status(200).json({
      success: true,
      message: 'Роль пользователя успешно обновлена',
      data: {
        userId: user._id,
        username: user.username,
        role: user.role
      }
    });
  } catch (error) {
    logger.error(`Ошибка при обновлении роли: ${error.message}`);
    
    return res.status(500).json({
      success: false,
      message: 'Ошибка при обновлении роли пользователя'
    });
  }
};

// Блокировка/разблокировка пользователя
const toggleUserBan = async (req, res) => {
  try {
    const { userId } = req.params;
    const { isBanned, banReason } = req.body;
    const adminUser = req.user;
    
    // Проверяем, что isBanned определен
    if (isBanned === undefined) {
      return res.status(400).json({
        success: false,
        message: 'Параметр isBanned обязателен'
      });
    }
    
    // Находим пользователя
    const user = await User.findById(userId);
    
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'Пользователь не найден'
      });
    }
    
    // Проверяем права на блокировку
    if (adminUser.role !== 'admin' && user.role === 'admin') {
      return res.status(403).json({
        success: false,
        message: 'У вас нет прав на блокировку администратора'
      });
    }
    
    // Обновляем статус блокировки
    user.isBanned = isBanned;
    user.banReason = isBanned ? banReason || 'Нарушение правил' : undefined;
    user.bannedBy = isBanned ? adminUser._id : undefined;
    
    await user.save();
    
    // Логирование
    await Log.logAdmin(
      isBanned ? 'ban_user' : 'unban_user',
      adminUser._id,
      user._id,
      'User',
      { banReason },
      req
    );
    
    return res.status(200).json({
      success: true,
      message: isBanned ? 'Пользователь заблокирован' : 'Пользователь разблокирован',
      data: {
        userId: user._id,
        username: user.username,
        isBanned: user.isBanned,
        banReason: user.banReason
      }
    });
  } catch (error) {
    logger.error(`Ошибка при блокировке/разблокировке: ${error.message}`);
    
    return res.status(500).json({
      success: false,
      message: 'Ошибка при изменении статуса блокировки пользователя'
    });
  }
};

// Сброс пароля пользователя
const resetUserPassword = async (req, res) => {
  try {
    const { userId } = req.params;
    const { newPassword } = req.body;
    const adminUser = req.user;
    
    if (!newPassword || newPassword.length < 6) {
      return res.status(400).json({
        success: false,
        message: 'Новый пароль должен содержать минимум 6 символов'
      });
    }
    
    // Находим пользователя
    const user = await User.findById(userId);
    
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'Пользователь не найден'
      });
    }
    
    // Проверяем права на сброс пароля
    if (adminUser.role !== 'admin' && user.role === 'admin') {
      return res.status(403).json({
        success: false,
        message: 'У вас нет прав на сброс пароля администратора'
      });
    }
    
    // Обновляем пароль
    user.password = newPassword;
    await user.save();
    
    // Логирование
    await Log.logAdmin(
      'reset_password',
      adminUser._id,
      user._id,
      'User',
      {},
      req
    );
    
    return res.status(200).json({
      success: true,
      message: 'Пароль пользователя успешно сброшен'
    });
  } catch (error) {
    logger.error(`Ошибка при сбросе пароля: ${error.message}`);
    
    return res.status(500).json({
      success: false,
      message: 'Ошибка при сбросе пароля пользователя'
    });
  }
};

// Удаление пользователя
const deleteUser = async (req, res) => {
  try {
    const { userId } = req.params;
    const adminUser = req.user;
    
    // Находим пользователя
    const user = await User.findById(userId);
    
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'Пользователь не найден'
      });
    }
    
    // Проверяем права на удаление
    if (adminUser.role !== 'admin' || user.role === 'admin') {
      return res.status(403).json({
        success: false,
        message: 'У вас нет прав на удаление этого пользователя'
      });
    }
    
    // Отзываем все активные ключи пользователя
    await Key.updateMany(
      { usedBy: user._id, status: 'used' },
      { status: 'revoked' }
    );
    
    // Отзываем все активные инвайты пользователя
    await Invite.updateMany(
      { createdBy: user._id, status: 'active' },
      { status: 'revoked' }
    );
    
    // Сохраняем информацию о пользователе для лога
    const userInfo = {
      username: user.username,
      email: user.email,
      role: user.role,
      discordId: user.discordId
    };
    
    // Удаляем пользователя
    await user.remove();
    
    // Логирование
    await Log.logAdmin(
      'delete_user',
      adminUser._id,
      userId,
      'User',
      userInfo,
      req
    );
    
    return res.status(200).json({
      success: true,
      message: 'Пользователь успешно удален'
    });
  } catch (error) {
    logger.error(`Ошибка при удалении пользователя: ${error.message}`);
    
    return res.status(500).json({
      success: false,
      message: 'Ошибка при удалении пользователя'
    });
  }
};

// Получение системных логов
const getLogs = async (req, res) => {
  try {
    const { page = 1, limit = 50, type, action, userId, startDate, endDate } = req.query;
    
    // Создаем условие для фильтрации
    const filter = {};
    
    if (type) filter.type = type;
    if (action) filter.action = action;
    if (userId) filter.userId = userId;
    
    // Фильтрация по дате
    if (startDate || endDate) {
      filter.createdAt = {};
      
      if (startDate) {
        filter.createdAt.$gte = new Date(startDate);
      }
      
      if (endDate) {
        filter.createdAt.$lte = new Date(endDate);
      }
    }
    
    // Получаем логи с пагинацией
    const logs = await Log.find(filter)
      .populate('userId', 'username')
      .sort({ createdAt: -1 })
      .skip((page - 1) * limit)
      .limit(parseInt(limit))
      .lean();
    
    // Получаем общее количество логов
    const total = await Log.countDocuments(filter);
    
    return res.status(200).json({
      success: true,
      data: {
        logs,
        pagination: {
          total,
          page: parseInt(page),
          limit: parseInt(limit),
          pages: Math.ceil(total / limit)
        }
      }
    });
  } catch (error) {
    logger.error(`Ошибка при получении логов: ${error.message}`);
    
    return res.status(500).json({
      success: false,
      message: 'Ошибка при получении системных логов'
    });
  }
};

// Получение системной статистики
const getStats = async (req, res) => {
  try {
    // Получаем общую статистику
    const totalUsers = await User.countDocuments();
    const totalActiveUsers = await User.countDocuments({
      isBanned: false,
      activeKeys: { $exists: true, $not: { $size: 0 } }
    });
    
    const totalKeys = await Key.countDocuments();
    const activeKeys = await Key.countDocuments({ status: 'active' });
    const usedKeys = await Key.countDocuments({ status: 'used' });
    
    // Статистика по ролям
    const usersByRole = await User.aggregate([
      { $group: { _id: '$role', count: { $sum: 1 } } }
    ]);
    
    // Статистика по ключам
    const keysByStatus = await Key.aggregate([
      { $group: { _id: '$status', count: { $sum: 1 } } }
    ]);
    
    // Статистика регистраций по дням (за последний месяц)
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    
    const registrationStats = await User.aggregate([
      {
        $match: {
          createdAt: { $gte: thirtyDaysAgo }
        }
      },
      {
        $group: {
          _id: {
            year: { $year: '$createdAt' },
            month: { $month: '$createdAt' },
            day: { $dayOfMonth: '$createdAt' }
          },
          count: { $sum: 1 }
        }
      },
      { $sort: { '_id.year': 1, '_id.month': 1, '_id.day': 1 } }
    ]);
    
    return res.status(200).json({
      success: true,
      data: {
        users: {
          total: totalUsers,
          activeUsers: totalActiveUsers,
          byRole: usersByRole.reduce((acc, item) => {
            acc[item._id] = item.count;
            return acc;
          }, {})
        },
        keys: {
          total: totalKeys,
          active: activeKeys,
          used: usedKeys,
          byStatus: keysByStatus.reduce((acc, item) => {
            acc[item._id] = item.count;
            return acc;
          }, {})
        },
        registrations: {
          last30Days: registrationStats.map(item => ({
            date: `${item._id.year}-${item._id.month}-${item._id.day}`,
            count: item.count
          }))
        }
      }
    });
  } catch (error) {
    logger.error(`Ошибка при получении статистики: ${error.message}`);
    
    return res.status(500).json({
      success: false,
      message: 'Ошибка при получении системной статистики'
    });
  }
};

module.exports = {
  getAllUsers,
  getUserById,
  updateUserRole,
  toggleUserBan,
  resetUserPassword,
  deleteUser,
  getLogs,
  getStats
}; 