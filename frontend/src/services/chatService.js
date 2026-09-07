import api from './api';

// Get all chats for the current user
export const getChats = async () => {
  const response = await api.get('/chats');
  return response.data;
};

// Create a new chat
export const createChat = async (title = 'New Chat') => {
  const response = await api.post('/chats', { title });
  return response.data;
};

// Get a single chat by ID
export const getChat = async (chatId) => {
  const response = await api.get(`/chats/${chatId}`);
  return response.data;
};

// Delete a chat by ID
export const deleteChat = async (chatId) => {
  const response = await api.delete(`/chats/${chatId}`);
  return response.data;
};
