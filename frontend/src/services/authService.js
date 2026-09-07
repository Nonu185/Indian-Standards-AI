import api from './api';

// Get the currently authenticated user
export const getMe = async () => {
  const response = await api.get('/auth/me');
  return response.data;
};

// Log out the current user
export const logout = async () => {
  const response = await api.post('/auth/logout');
  return response.data;
};

// Get the Google OAuth login URL
export const getGoogleLoginUrl = () => {
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:5001/api';
  return `${baseUrl}/auth/google`;
};
