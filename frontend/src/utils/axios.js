import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:5000/api', 
});

api.interceptors.request.use(config => {
  // Look for the ticket under both common names!
  const token = localStorage.getItem('token') || localStorage.getItem('access_token'); 
  
  // Make sure it is a REAL ticket, not just the word "undefined" or "null"
  if (token && token !== 'undefined' && token !== 'null') {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;