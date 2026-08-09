import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8001',
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
