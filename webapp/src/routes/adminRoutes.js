const express = require('express');
const router = express.Router();
const adminController = require('../controllers/adminController');
const { authenticate, authorize } = require('../middlewares/auth');

// Админский доступ для всех маршрутов
router.use(authenticate, authorize(['admin']));

// Управление пользователями
router.get('/users', adminController.getAllUsers);
router.get('/users/:userId', adminController.getUserById);
router.put('/users/:userId/role', adminController.updateUserRole);
router.put('/users/:userId/ban', adminController.toggleUserBan);
router.put('/users/:userId/password', adminController.resetUserPassword);
router.delete('/users/:userId', adminController.deleteUser);

// Логи и статистика
router.get('/logs', adminController.getLogs);
router.get('/stats', adminController.getStats);

module.exports = router; 