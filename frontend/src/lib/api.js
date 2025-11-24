import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000';

const getAuthHeaders = () => {
  const token = localStorage.getItem('trackflow_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export const api = {
  async register(email, password, name) {
    const response = await axios.post(`${API_URL}/api/register`, { email, password, name });
    if (response.data.token) {
      localStorage.setItem('trackflow_token', response.data.token);
      localStorage.setItem('trackflow_user', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  async login(email, password) {
    const response = await axios.post(`${API_URL}/api/login`, { email, password });
    if (response.data.token) {
      localStorage.setItem('trackflow_token', response.data.token);
      localStorage.setItem('trackflow_user', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  logout() {
    localStorage.removeItem('trackflow_token');
    localStorage.removeItem('trackflow_user');
  },

  async getMe() {
    const response = await axios.get(`${API_URL}/api/me`, {
      headers: getAuthHeaders()
    });
    return response.data;
  },

  async uploadAndProcess(file) {
    const formData = new FormData();
    formData.append('video', file);
    
    const response = await axios.post(`${API_URL}/api/process`, formData, {
      headers: { 
        'Content-Type': 'multipart/form-data',
        ...getAuthHeaders()
      }
    });
    return response.data;
  },

  async getProcess(id) {
    const response = await axios.get(`${API_URL}/api/processes/${id}`, {
      headers: getAuthHeaders()
    });
    return response.data;
  },

  async getProcesses() {
    const response = await axios.get(`${API_URL}/api/processes`, {
      headers: getAuthHeaders()
    });
    return response.data;
  },

  async getHistory() {
    const response = await axios.get(`${API_URL}/api/history`, {
      headers: getAuthHeaders()
    });
    return response.data;
  },

  async deleteHistory(id) {
    const response = await axios.delete(`${API_URL}/api/history/${id}`, {
      headers: getAuthHeaders()
    });
    return response.data;
  }
};
