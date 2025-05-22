const express = require('express');
const router = express.Router();
const adminController = require('../controllers/adminController');
const { authenticate, authorize } = require('../middlewares/auth');

// Модераторский доступ для всех маршрутов
router.use(authenticate, authorize(['admin', 'moderator']));

// Управление пользователями (ограниченное)
router.get('/users', adminController.getAllUsers);
router.get('/users/:userId', adminController.getUserById);

// Модератор может управлять обычными пользователями
router.put('/users/:userId/ban', adminController.toggleUserBan);

module.exports = router; 