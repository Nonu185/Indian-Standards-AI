import api from './api';

// Get all messages for a chat
export const getMessages = async (chatId) => {
  const response = await api.get(`/chats/${chatId}/messages`);
  return response.data;
};

// Send a message and get a mock AI response
export const sendMessage = async (chatId, content) => {
  const response = await api.post(`/chats/${chatId}/messages`, { content });
  return response.data;
};
