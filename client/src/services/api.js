import axios from 'axios';

const BASE_URL =
  import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && !error.config?.url?.includes('/auth/login')) {
      clearTokens();
    }
    return Promise.reject(error);
  }
);

export const clearTokens = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
};

export const setTokens = (accessToken) => {
  localStorage.setItem('access_token', accessToken);
};

export default api;
