const mongoose = require('mongoose');
const crypto = require('crypto');

// Схема ключа доступа
const keySchema = new mongoose.Schema({
  // Сам ключ (уникальный)
  code: {
    type: String,
    required: true,
    unique: true,
    default: () => crypto.randomBytes(16).toString('hex')
  },
  // Статус ключа
  status: {
    type: String,
    enum: ['active', 'used', 'expired', 'revoked'],
    default: 'active'
  },
  // Тип ключа (может быть использован для разных продуктов/уровней доступа)
  type: {
    type: String,
    enum: ['default'],
    default: 'default'
  },
  // Кто создал ключ
  createdBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  // Кто использовал ключ
  usedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },
  // Дата активации (привязки к пользователю)
  activatedAt: Date,
  // Срок действия (в секундах, от момента активации)
  duration: {
    type: Number,
    default: 30 * 24 * 60 * 60 // 30 дней по умолчанию
  },
  // Дата истечения срока действия
  expiresAt: Date,
  // Метаданные ключа (дополнительная информация)
  metadata: {
    type: mongoose.Schema.Types.Mixed,
    default: {}
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

// Методы для работы с ключами
keySchema.methods.activate = function(userId) {
  if (this.status !== 'active') {
    throw new Error('Ключ уже использован или истек');
  }
  
  this.status = 'used';
  this.usedBy = userId;
  this.activatedAt = new Date();
  this.expiresAt = new Date(Date.now() + this.duration * 1000);
  
  return this.save();
};

keySchema.methods.isExpired = function() {
  if (!this.expiresAt) return false;
  return new Date() > this.expiresAt;
};

// Обновление статуса ключа на 'expired', если срок действия истек
keySchema.methods.updateStatus = function() {
  if (this.status === 'used' && this.isExpired()) {
    this.status = 'expired';
    return this.save();
  }
  return Promise.resolve(this);
};

// Статический метод для генерации нового ключа
keySchema.statics.generateKey = function(createdBy, options = {}) {
  return this.create({
    createdBy,
    type: options.type || 'default',
    duration: options.duration || 30 * 24 * 60 * 60,
    metadata: options.metadata || {}
  });
};

// Статический метод для поиска активного ключа по коду
keySchema.statics.findActiveKeyByCode = function(code) {
  return this.findOne({ code, status: 'active' });
};

// Статический метод для поиска всех ключей, созданных определенным пользователем
keySchema.statics.findKeysByCreator = function(userId) {
  return this.find({ createdBy: userId }).sort({ createdAt: -1 });
};

const Key = mongoose.model('Key', keySchema);

module.exports = Key; 