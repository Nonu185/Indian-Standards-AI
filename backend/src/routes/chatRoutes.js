const express = require('express');
const { getChats, createChat, getChat, deleteChat } = require('../controllers/chatController');
const { requireAuth } = require('../middleware/auth');

const router = express.Router();

// All chat routes require authentication
router.use(requireAuth);

// GET /api/chats — list all chats for the logged-in user
router.get('/', getChats);

// POST /api/chats — create a new chat
router.post('/', createChat);

// GET /api/chats/:chatId — get a specific chat
router.get('/:chatId', getChat);

// DELETE /api/chats/:chatId — delete a specific chat
router.delete('/:chatId', deleteChat);

module.exports = router;
