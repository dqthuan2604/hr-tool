import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});

export const templatesApi = {
  // Add methods later
};

export const candidatesApi = {
  // Add methods later
};

export const generatorApi = {
  // Add methods later
};

export default api;
