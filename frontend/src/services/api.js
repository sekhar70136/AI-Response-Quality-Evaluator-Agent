import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 60000,
});

export const evaluateResponse = async (payload) => {
  const response = await api.post('/evaluate', payload);
  return response.data;
};

export const evaluateBatch = async (payload) => {
  const response = await api.post('/evaluate/batch', payload);
  return response.data;
};
