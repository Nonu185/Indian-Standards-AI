import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5001/api',
  withCredentials: true, // send cookies with every request (needed for sessions)
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
