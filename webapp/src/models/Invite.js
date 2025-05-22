const mongoose = require('mongoose');
const crypto = require('crypto');

// Схема инвайт-кода
const inviteSchema = new mongoose.Schema({
  // Код приглашения
  code: {
    type: String,
    required: true,
    unique: true,
    default: () => crypto.randomBytes(8).toString('hex')
  },
  // Создатель приглашения
  createdBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  // Статус приглашения
  status: {
    type: String,
    enum: ['active', 'used', 'expired', 'revoked'],
    default: 'active'
  },
  // Пользователь, который воспользовался приглашением
  usedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },
  // Дата использования
  usedAt: Date,
  // Срок действия приглашения
  expiresAt: {
    type: Date,
    default: () => new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) // 7 дней по умолчанию
  },
  // Роль, которая будет присвоена пользователю при регистрации
  role: {
    type: String,
    enum: ['user', 'moderator', 'admin'],
    default: 'user'
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: true
});

// Проверка, истекло ли приглашение
inviteSchema.methods.isExpired = function() {
  return new Date() > this.expiresAt;
};

// Использование приглашения
inviteSchema.methods.use = function(userId) {
  if (this.status !== 'active') {
    throw new Error('Приглашение уже использовано или истекло');
  }
  
  if (this.isExpired()) {
    this.status = 'expired';
    throw new Error('Срок действия приглашения истек');
  }
  
  this.status = 'used';
  this.usedBy = userId;
  this.usedAt = new Date();
  
  return this.save();
};

// Статический метод для генерации нового приглашения
inviteSchema.statics.generateInvite = async function(createdBy, options = {}) {
  // Проверяем, есть ли у пользователя доступные инвайты
  const creator = await mongoose.model('User').findById(createdBy);
  
  if (!creator) {
    throw new Error('Пользователь не найден');
  }
  
  creator.resetInvitesIfNeeded();
  
  if (creator.invitesLeft <= 0 && creator.role !== 'admin') {
    throw new Error('У вас закончились доступные приглашения');
  }
  
  // Создаем приглашение
  const invite = await this.create({
    createdBy,
    role: options.role || 'user',
    expiresAt: options.expiresAt || new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
  });
  
  // Уменьшаем счетчик доступных инвайтов
  if (creator.role !== 'admin') {
    creator.invitesLeft -= 1;
    await creator.save();
  }
  
  return invite;
};

// Статический метод для проверки валидности кода приглашения
inviteSchema.statics.findActiveByCode = function(code) {
  return this.findOne({ 
    code, 
    status: 'active',
    expiresAt: { $gt: new Date() }
  });
};

const Invite = mongoose.model('Invite', inviteSchema);

module.exports = Invite; 