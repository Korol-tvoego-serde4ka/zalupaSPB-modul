const mongoose = require('mongoose');

// Схема логов системы
const logSchema = new mongoose.Schema({
  // Тип события
  type: {
    type: String,
    enum: [
      'auth', // Аутентификация (вход, выход)
      'user', // Действия с пользователями (создание, удаление, изменение)
      'key', // Действия с ключами (создание, активация, удаление)
      'invite', // Действия с инвайтами (создание, использование)
      'discord', // Связь с Discord (связывание, отвязка)
      'admin', // Административные действия
      'system' // Системные события
    ],
    required: true
  },
  // Подтип события
  action: {
    type: String,
    required: true
  },
  // Пользователь, выполнивший действие
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },
  // ID сущности, с которой выполнялось действие
  targetId: mongoose.Schema.Types.ObjectId,
  // Тип сущности
  targetType: String,
  // Метаданные лога (дополнительная информация)
  metadata: {
    type: mongoose.Schema.Types.Mixed,
    default: {}
  },
  // IP адрес
  ip: String,
  // User-Agent
  userAgent: String,
  createdAt: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: { createdAt: true, updatedAt: false }
});

// Создание индексов для быстрого поиска
logSchema.index({ type: 1 });
logSchema.index({ userId: 1 });
logSchema.index({ createdAt: -1 });

// Статический метод для создания записи в логе
logSchema.statics.createLog = function(data) {
  return this.create(data);
};

// Метод для добавления лога аутентификации
logSchema.statics.logAuth = function(action, userId, metadata = {}, req = null) {
  return this.createLog({
    type: 'auth',
    action,
    userId,
    metadata,
    ip: req ? req.ip : null,
    userAgent: req && req.headers ? req.headers['user-agent'] : null
  });
};

// Метод для добавления лога действия с пользователем
logSchema.statics.logUser = function(action, userId, targetId, metadata = {}, req = null) {
  return this.createLog({
    type: 'user',
    action,
    userId,
    targetId,
    targetType: 'User',
    metadata,
    ip: req ? req.ip : null,
    userAgent: req && req.headers ? req.headers['user-agent'] : null
  });
};

// Метод для добавления лога действия с ключом
logSchema.statics.logKey = function(action, userId, keyId, metadata = {}, req = null) {
  return this.createLog({
    type: 'key',
    action,
    userId,
    targetId: keyId,
    targetType: 'Key',
    metadata,
    ip: req ? req.ip : null,
    userAgent: req && req.headers ? req.headers['user-agent'] : null
  });
};

// Метод для добавления лога действия с инвайтом
logSchema.statics.logInvite = function(action, userId, inviteId, metadata = {}, req = null) {
  return this.createLog({
    type: 'invite',
    action,
    userId,
    targetId: inviteId,
    targetType: 'Invite',
    metadata,
    ip: req ? req.ip : null,
    userAgent: req && req.headers ? req.headers['user-agent'] : null
  });
};

// Метод для добавления лога действия с Discord
logSchema.statics.logDiscord = function(action, userId, metadata = {}, req = null) {
  return this.createLog({
    type: 'discord',
    action,
    userId,
    metadata,
    ip: req ? req.ip : null,
    userAgent: req && req.headers ? req.headers['user-agent'] : null
  });
};

// Метод для добавления лога административного действия
logSchema.statics.logAdmin = function(action, userId, targetId, targetType, metadata = {}, req = null) {
  return this.createLog({
    type: 'admin',
    action,
    userId,
    targetId,
    targetType,
    metadata,
    ip: req ? req.ip : null,
    userAgent: req && req.headers ? req.headers['user-agent'] : null
  });
};

// Метод для добавления системного лога
logSchema.statics.logSystem = function(action, metadata = {}) {
  return this.createLog({
    type: 'system',
    action,
    metadata
  });
};

const Log = mongoose.model('Log', logSchema);

module.exports = Log; 