import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000';

export const api = {
  async uploadAndProcess(file) {
    const formData = new FormData();
    formData.append('video', file);
    
    const response = await axios.post(`${API_URL}/api/process`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  async getProcess(id) {
    const response = await axios.get(`${API_URL}/api/processes/${id}`);
    return response.data;
  },

  async getProcesses() {
    const response = await axios.get(`${API_URL}/api/processes`);
    return response.data;
  },

  async getHistory() {
    const response = await axios.get(`${API_URL}/api/history`);
    return response.data;
  },

  async deleteHistory(id) {
    const response = await axios.delete(`${API_URL}/api/history/${id}`);
    return response.data;
  }
};
