import api from './api';

// Get all messages for a chat
export const getMessages = async (chatId) => {
  const response = await api.get(`/chats/${chatId}/messages`);
  return response.data;
};

// Send a user message and persist the AI result alongside it.
// aiResult is optional: { summary, recommendations, extractedRequirements }
export const sendMessage = async (chatId, content, aiResult = null) => {
  const payload = { content };
  if (aiResult?.recommendations?.length > 0) {
    // The controller reads 'content' as the assistant summary too,
    // so we pass the AI summary as content for the assistant slot.
    payload.content = aiResult.summary || content;
    payload.recommendations = aiResult.recommendations;
    payload.extractedRequirements = aiResult.extractedRequirements ?? null;
  }
  const response = await api.post(`/chats/${chatId}/messages`, payload);
  return response.data;
};
