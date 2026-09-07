const express = require('express');

const {
  getMessages,
  sendMessage
} = require('../controllers/messageController');

const { requireAuth } = require('../middleware/auth');

const router = express.Router();

router.use(requireAuth);

router.get('/:chatId/messages', getMessages);

router.post('/:chatId/messages', sendMessage);

module.exports = router;