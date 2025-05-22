const express = require('express');
const router = express.Router();
const discordController = require('../controllers/discordController');
const { authenticate } = require('../middlewares/auth');

// Маршруты для пользователей сайта
router.get('/link/status', authenticate, discordController.checkLinkStatus);
router.post('/link/generate', authenticate, discordController.generateLinkCode);
router.post('/unlink', authenticate, discordController.unlinkDiscord);

// API для Discord бота
router.post('/bot/link', discordController.linkByCode);
router.get('/bot/user/:discordId', discordController.getUserByDiscordId);

module.exports = router; 