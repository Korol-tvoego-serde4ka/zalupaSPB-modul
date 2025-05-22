const express = require('express');
const router = express.Router();
const inviteController = require('../controllers/inviteController');
const { authenticate, authorize } = require('../middlewares/auth');

// Публичные маршруты
router.post('/check', inviteController.checkInviteCode);

// Защищенные маршруты
router.post('/create', authenticate, inviteController.createInvite);
router.get('/my', authenticate, inviteController.getMyInvites);
router.get('/invited-users', authenticate, inviteController.getInvitedUsers);

// Управление инвайтами
router.delete('/:inviteId/revoke', authenticate, inviteController.revokeInvite);

// Админские маршруты
router.get('/', authenticate, authorize(['admin', 'moderator']), inviteController.getAllInvites);

module.exports = router; 