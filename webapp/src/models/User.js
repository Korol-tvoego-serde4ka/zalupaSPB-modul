const mongoose = require('mongoose');
const bcrypt = require('bcrypt');

// Схема пользователя
const userSchema = new mongoose.Schema({
  username: {
    type: String,
    required: true,
    unique: true,
    trim: true,
    minlength: 3,
    maxlength: 30
  },
  password: {
    type: String,
    required: true,
    minlength: 6
  },
  email: {
    type: String,
    required: true,
    unique: true,
    trim: true,
    lowercase: true
  },
  role: {
    type: String,
    enum: ['user', 'moderator', 'admin'],
    default: 'user'
  },
  // Привязка к Discord
  discordId: {
    type: String,
    sparse: true,
    unique: true
  },
  discordUsername: String,
  // Счетчик доступных инвайтов
  invitesLeft: {
    type: Number,
    default: function() {
      if (this.role === 'admin') return Number.MAX_SAFE_INTEGER;
      if (this.role === 'moderator') return 10;
      return 2; // Для обычных пользователей
    }
  },
  // Дата последнего обновления инвайтов
  lastInviteReset: {
    type: Date,
    default: Date.now
  },
  // Приглашен кем
  invitedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },
  // Список кого пригласил этот пользователь
  invitedUsers: [{
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  }],
  // Активные ключи пользователя
  activeKeys: [{
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Key'
  }],
  // Заблокирован ли пользователь
  isBanned: {
    type: Boolean,
    default: false
  },
  // Причина блокировки
  banReason: String,
  // Кем заблокирован
  bannedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
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

// Хеширование пароля перед сохранением
userSchema.pre('save', async function(next) {
  const user = this;
  if (!user.isModified('password')) return next();
  
  try {
    const salt = await bcrypt.genSalt(10);
    user.password = await bcrypt.hash(user.password, salt);
    next();
  } catch (error) {
    next(error);
  }
});

// Метод для проверки пароля
userSchema.methods.comparePassword = async function(candidatePassword) {
  return bcrypt.compare(candidatePassword, this.password);
};

// Сброс количества инвайтов в начале месяца для обычных пользователей
userSchema.methods.resetInvitesIfNeeded = function() {
  const now = new Date();
  const lastReset = new Date(this.lastInviteReset);
  
  // Если прошел месяц с последнего сброса
  if (now.getMonth() !== lastReset.getMonth() || now.getFullYear() !== lastReset.getFullYear()) {
    if (this.role === 'user') {
      this.invitesLeft = 2;
    } else if (this.role === 'moderator') {
      this.invitesLeft = 10;
    }
    this.lastInviteReset = now;
  }
};

const User = mongoose.model('User', userSchema);

module.exports = User; 