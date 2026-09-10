const Chat = require('../models/Chat');
const Message = require('../models/Message');
const { generateChatTitle } = require('../services/ai/mistralService');

// Helper — verify chat belongs to the authenticated user
const verifyChat = async (chatId, userId) => {
  const chat = await Chat.findOne({ _id: chatId, userId });
  return chat;
};

// GET /api/chats/:chatId/messages — get all messages for a specific chat
const getMessages = async (req, res) => {
  try {
    const chat = await verifyChat(req.params.chatId, req.user._id);
    if (!chat) {
      return res.status(404).json({ error: 'Chat not found' });
    }

    const messages = await Message.find({ chatId: req.params.chatId }).sort({ createdAt: 1 });
    res.json(messages);
  } catch (error) {
    console.error('Error fetching messages:', error);
    res.status(500).json({ error: 'Failed to fetch messages' });
  }
};

const sendMessage = async (req, res) => {
  try {
    const { content, recommendations, extractedRequirements } = req.body;

    if (!content || content.trim() === '') {
      return res.status(400).json({ error: 'Message content cannot be empty' });
    }

    // Verify chat belongs to user
    const chat = await verifyChat(req.params.chatId, req.user._id);
    if (!chat) {
      return res.status(404).json({ error: 'Chat not found' });
    }

    // 1. Save the user's message
    const userMessage = await Message.create({
      chatId: req.params.chatId,
      userId: req.user._id,
      role: 'user',
      content: content.trim(),
    });

    // 2. Build and save the assistant's response.
    // If the caller provides a real AI summary + recommendations, persist them.
    // Otherwise fall back to the placeholder text.
    const hasAIResult = Array.isArray(recommendations) && recommendations.length > 0;
    const assistantContent = content.trim(); // caller sends the summary as content
    const assistantPayload = {
      chatId: req.params.chatId,
      userId: req.user._id,
      role: 'assistant',
      content: hasAIResult
        ? assistantContent
        : 'Your requirement has been received. The Indian Standards recommendation engine will analyze this requirement in the next phase.',
    };
    if (hasAIResult) {
      assistantPayload.recommendations = recommendations;
    }
    if (extractedRequirements) {
      assistantPayload.extractedRequirements = extractedRequirements;
    }
    const assistantMessage = await Message.create(assistantPayload);

    // 4. Update the chat title from the first user message if it's still "New Chat"
    let updatedChatTitle = null;
    if (chat.title === 'New Chat') {
      updatedChatTitle = await generateChatTitle(content.trim());
      
      // Fallback if Mistral fails
      if (!updatedChatTitle) {
        updatedChatTitle = content.trim().slice(0, 50);
      }

      await Chat.findByIdAndUpdate(req.params.chatId, {
        title: updatedChatTitle,
        updatedAt: new Date(),
      });
    } else {
      // Update updatedAt to keep the chat sorted correctly
      await Chat.findByIdAndUpdate(req.params.chatId, { updatedAt: new Date() });
    }

    // 5. Return both messages and the chat (if title was updated)
    res.status(201).json({
      userMessage,
      assistantMessage,
      ...(updatedChatTitle && { chat: { _id: chat._id, title: updatedChatTitle } }),
    });
  } catch (error) {
    console.error('Error sending message:', error);
    res.status(500).json({ error: 'Failed to send message. Please try again.' });
  }
};

module.exports = { getMessages, sendMessage };
