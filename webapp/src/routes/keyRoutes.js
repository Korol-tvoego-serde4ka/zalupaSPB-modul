const express = require('express');
const router = express.Router();
const keyController = require('../controllers/keyController');
const { authenticate, authorize, requireActiveKey } = require('../middlewares/auth');

// Защищенные маршруты
router.post('/generate', authenticate, authorize(['admin', 'moderator']), keyController.generateKey);
router.get('/my', authenticate, keyController.getMyKeys);
router.post('/activate', authenticate, keyController.activateKey);
router.get('/status', authenticate, keyController.checkKeyStatus);

// Админские маршруты
router.get('/', authenticate, authorize(['admin', 'moderator']), keyController.getAllKeys);
router.get('/:keyId', authenticate, authorize(['admin', 'moderator']), keyController.getKeyById);
router.delete('/:keyId/revoke', authenticate, authorize(['admin', 'moderator']), keyController.revokeKey);

module.exports = router; 