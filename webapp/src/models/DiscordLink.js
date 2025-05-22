const mongoose = require('mongoose');
const crypto = require('crypto');

// Схема для связи аккаунта сайта с Discord
const discordLinkSchema = new mongoose.Schema({
  // Код для связки аккаунтов
  code: {
    type: String,
    required: true,
    unique: true,
    default: () => crypto.randomBytes(4).toString('hex').toUpperCase()
  },
  // Пользователь сайта
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  // Статус кода
  status: {
    type: String,
    enum: ['active', 'used', 'expired'],
    default: 'active'
  },
  // Discord ID пользователя (после связывания)
  discordId: String,
  // Discord имя пользователя (после связывания)
  discordUsername: String,
  // Время истечения кода (15 минут)
  expiresAt: {
    type: Date,
    default: () => new Date(Date.now() + 15 * 60 * 1000)
  },
  // Дата использования
  usedAt: Date,
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

// Проверка, истек ли код
discordLinkSchema.methods.isExpired = function() {
  return new Date() > this.expiresAt;
};

// Использование кода связи
discordLinkSchema.methods.use = function(discordId, discordUsername) {
  if (this.status !== 'active') {
    throw new Error('Код уже использован или истек');
  }
  
  if (this.isExpired()) {
    this.status = 'expired';
    throw new Error('Срок действия кода истек');
  }
  
  this.status = 'used';
  this.discordId = discordId;
  this.discordUsername = discordUsername;
  this.usedAt = new Date();
  
  return this.save();
};

// Статический метод для генерации нового кода связи
discordLinkSchema.statics.generateLink = async function(userId) {
  // Удаляем все предыдущие активные коды для этого пользователя
  await this.updateMany(
    { userId, status: 'active' },
    { status: 'expired' }
  );
  
  // Создаем новый код
  return this.create({ userId });
};

// Статический метод для поиска активного кода по значению
discordLinkSchema.statics.findActiveByCode = function(code) {
  return this.findOne({ 
    code, 
    status: 'active',
    expiresAt: { $gt: new Date() }
  });
};

const DiscordLink = mongoose.model('DiscordLink', discordLinkSchema);

module.exports = DiscordLink; 