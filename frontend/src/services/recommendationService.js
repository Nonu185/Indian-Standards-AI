import api from './api';

/**
 * Send a natural-language procurement requirement to the AI recommendation endpoint.
 * Returns { success, query, extracted_requirements, recommendations }
 */
export const getRecommendations = async (requirement) => {
  const response = await api.post('/recommendations', { text: requirement });
  return response.data;
};
