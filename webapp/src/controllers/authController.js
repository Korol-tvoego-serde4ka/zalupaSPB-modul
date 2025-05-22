const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const User = require('../models/User');
const Invite = require('../models/Invite');
const Log = require('../models/Log');
const config = require('../config/config');
const logger = require('../config/logger');

// Генерация JWT токенов
const generateTokens = (userId) => {
  const accessToken = jwt.sign({ id: userId }, config.jwt.secret, {
    expiresIn: config.jwt.accessExpiresIn
  });
  
  const refreshToken = jwt.sign({ id: userId }, config.jwt.secret, {
    expiresIn: config.jwt.refreshExpiresIn
  });
  
  return { accessToken, refreshToken };
};

// Регистрация нового пользователя
const register = async (req, res) => {
  try {
    const { username, email, password, inviteCode } = req.body;
    
    // Проверяем, что все необходимые поля заполнены
    if (!username || !email || !password || !inviteCode) {
      return res.status(400).json({
        success: false,
        message: 'Пожалуйста, заполните все поля'
      });
    }
    
    // Проверяем, что пользователь с таким именем или email не существует
    const existingUser = await User.findOne({
      $or: [{ username }, { email }]
    });
    
    if (existingUser) {
      return res.status(400).json({
        success: false,
        message: 'Пользователь с таким именем или email уже существует'
      });
    }
    
    // Проверяем инвайт-код
    const invite = await Invite.findActiveByCode(inviteCode);
    
    if (!invite) {
      return res.status(400).json({
        success: false,
        message: 'Недействительный или истекший инвайт-код'
      });
    }
    
    // Создаем нового пользователя
    const user = new User({
      username,
      email,
      password,
      role: invite.role,
      invitedBy: invite.createdBy
    });
    
    await user.save();
    
    // Использование инвайт-кода
    await invite.use(user._id);
    
    // Обновление данных создателя инвайта
    await User.findByIdAndUpdate(invite.createdBy, {
      $push: { invitedUsers: user._id }
    });
    
    // Логирование
    await Log.logUser('register', user._id, user._id, { inviteCode }, req);
    await Log.logInvite('use', user._id, invite._id, {}, req);
    
    // Генерация JWT токенов
    const tokens = generateTokens(user._id);
    
    return res.status(201).json({
      success: true,
      message: 'Пользователь успешно зарегистрирован',
      data: {
        user: {
          id: user._id,
          username: user.username,
          role: user.role
        },
        tokens
      }
    });
  } catch (error) {
    logger.error(`Ошибка при регистрации: ${error.message}`);
    
    return res.status(500).json({
      success: false,
      message: 'Ошибка при регистрации пользователя'
    });
  }
};

// Авторизация пользователя
const login = async (req, res) => {
  try {
    const { username, password } = req.body;
    
    // Проверяем, что все необходимые поля заполнены
    if (!username || !password) {
      return res.status(400).json({
        success: false,
        message: 'Пожалуйста, заполните все поля'
      });
    }
    
    // Ищем пользователя по имени или email
    const user = await User.findOne({
      $or: [
        { username },
        { email: username.toLowerCase() }
      ]
    });
    
    if (!user) {
      return res.status(401).json({
        success: false,
        message: 'Неверное имя пользователя или пароль'
      });
    }
    
    // Проверяем, заблокирован ли пользователь
    if (user.isBanned) {
      return res.status(403).json({
        success: false,
        message: 'Аккаунт заблокирован',
        banReason: user.banReason
      });
    }
    
    // Проверяем пароль
    const isPasswordValid = await user.comparePassword(password);
    
    if (!isPasswordValid) {
      return res.status(401).json({
        success: false,
        message: 'Неверное имя пользователя или пароль'
      });
    }
    
    // Генерация JWT токенов
    const tokens = generateTokens(user._id);
    
    // Логирование
    await Log.logAuth('login', user._id, {}, req);
    
    return res.status(200).json({
      success: true,
      message: 'Авторизация успешна',
      data: {
        user: {
          id: user._id,
          username: user.username,
          role: user.role
        },
        tokens
      }
    });
  } catch (error) {
    logger.error(`Ошибка при авторизации: ${error.message}`);
    
    return res.status(500).json({
      success: false,
      message: 'Ошибка при авторизации пользователя'
    });
  }
};

// Обновление токена доступа
const refreshToken = async (req, res) => {
  try {
    const { refreshToken } = req.body;
    
    if (!refreshToken) {
      return res.status(400).json({
        success: false,
        message: 'Требуется токен обновления'
      });
    }
    
    // Верифицируем refresh токен
    const decoded = jwt.verify(refreshToken, config.jwt.secret);
    
    // Ищем пользователя
    const user = await User.findById(decoded.id);
    
    if (!user) {
      return res.status(401).json({
        success: false,
        message: 'Недействительный токен'
      });
    }
    
    // Проверяем, заблокирован ли пользователь
    if (user.isBanned) {
      return res.status(403).json({
        success: false,
        message: 'Аккаунт заблокирован',
        banReason: user.banReason
      });
    }
    
    // Генерация новых JWT токенов
    const tokens = generateTokens(user._id);
    
    return res.status(200).json({
      success: true,
      message: 'Токены успешно обновлены',
      data: { tokens }
    });
  } catch (error) {
    if (error.name === 'JsonWebTokenError' || error.name === 'TokenExpiredError') {
      return res.status(401).json({
        success: false,
        message: 'Недействительный или истекший токен'
      });
    }
    
    logger.error(`Ошибка при обновлении токена: ${error.message}`);
    
    return res.status(500).json({
      success: false,
      message: 'Ошибка при обновлении токена'
    });
  }
};

// Получение информации о текущем пользователе
const me = async (req, res) => {
  try {
    // Получаем пользователя из middleware authenticate
    const user = req.user;
    
    // Проверяем количество доступных инвайтов
    user.resetInvitesIfNeeded();
    await user.save();
    
    return res.status(200).json({
      success: true,
      data: {
        user: {
          id: user._id,
          username: user.username,
          email: user.email,
          role: user.role,
          discordId: user.discordId,
          discordUsername: user.discordUsername,
          invitesLeft: user.invitesLeft,
          createdAt: user.createdAt
        }
      }
    });
  } catch (error) {
    logger.error(`Ошибка при получении информации о пользователе: ${error.message}`);
    
    return res.status(500).json({
      success: false,
      message: 'Ошибка при получении информации о пользователе'
    });
  }
};

// Изменение пароля
const changePassword = async (req, res) => {
  try {
    const { currentPassword, newPassword } = req.body;
    const user = req.user;
    
    if (!currentPassword || !newPassword) {
      return res.status(400).json({
        success: false,
        message: 'Пожалуйста, заполните все поля'
      });
    }
    
    // Проверяем текущий пароль
    const isPasswordValid = await user.comparePassword(currentPassword);
    
    if (!isPasswordValid) {
      return res.status(401).json({
        success: false,
        message: 'Неверный текущий пароль'
      });
    }
    
    // Обновляем пароль
    user.password = newPassword;
    await user.save();
    
    // Логирование
    await Log.logUser('change_password', user._id, user._id, {}, req);
    
    return res.status(200).json({
      success: true,
      message: 'Пароль успешно изменен'
    });
  } catch (error) {
    logger.error(`Ошибка при изменении пароля: ${error.message}`);
    
    return res.status(500).json({
      success: false,
      message: 'Ошибка при изменении пароля'
    });
  }
};

module.exports = {
  register,
  login,
  refreshToken,
  me,
  changePassword
}; 