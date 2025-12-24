import axios from 'axios';
import { uploadVideoToStorage } from './supabase.js';

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

  async uploadAndProcess(file, lineCoordinates = null, onUploadProgress = null) {
    // Direct upload to Railway backend (works better for large files)
    const formData = new FormData();
    formData.append('video', file);
    
    // Add line coordinates if provided
    if (lineCoordinates) {
      formData.append('line_x1', lineCoordinates.x1);
      formData.append('line_y1', lineCoordinates.y1);
      formData.append('line_x2', lineCoordinates.x2);
      formData.append('line_y2', lineCoordinates.y2);
    }
    
    const response = await axios.post(`${API_URL}/api/process`, formData, {
      headers: { 
        'Content-Type': 'multipart/form-data',
        ...getAuthHeaders()
      },
      timeout: 600000, // 10 minute timeout for upload
      maxContentLength: Infinity,
      maxBodyLength: Infinity,
      onUploadProgress: (progressEvent) => {
        if (onUploadProgress && progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onUploadProgress(percentCompleted);
        }
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
    console.log('API: Calling getHistory...')
    console.log('API: Headers:', getAuthHeaders())
    const response = await axios.get(`${API_URL}/api/history`, {
      headers: getAuthHeaders()
    });
    console.log('API: History response:', response.data)
    return response.data;
  },

  async deleteHistory(id) {
    const response = await axios.delete(`${API_URL}/api/history/${id}`, {
      headers: getAuthHeaders()
    });
    return response.data;
  }
};
