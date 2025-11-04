// frontend-react/src/api/apiClient.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar el token de autenticación
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar errores de respuesta
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

const api = {
  // ==================== AUTENTICACIÓN ====================
  // ==================== AUTENTICACIÓN ====================
  login: (username, password) => {
    return apiClient.post('/auth/login', {}, {
      params: { username, password }
    }).then(res => res.data);
  },

  // ==================== CONVERSACIONES ====================
  getConversations: (params) => apiClient.get('/admin/conversations', { params }).then(res => res.data),
  getConversation: (id) => apiClient.get(`/admin/conversations/${id}`).then(res => res.data),
  getMessages: (conversationId) => apiClient.get(`/admin/conversations/${conversationId}/messages`).then(res => res.data),
  updateConversationStatus: (id, status) => apiClient.put(`/admin/conversations/${id}/status`, null, { params: { status } }).then(res => res.data),

  // ==================== LEADS ====================
  getLeads: (params) => apiClient.get('/admin/leads', { params }).then(res => res.data),
  getLead: (id) => apiClient.get(`/admin/leads/${id}`).then(res => res.data),
  updateLead: (id, data) => apiClient.put(`/admin/leads/${id}`, null, { params: data }).then(res => res.data),
  convertLead: (id) => apiClient.post(`/admin/leads/${id}/convert`).then(res => res.data),

  // ==================== DISTRIBUIDORES ====================
  getDistributors: (params) => apiClient.get('/distributors', { params }).then(res => res.data),
  getDistributor: (id) => apiClient.get(`/distributors/${id}`).then(res => res.data),
  createDistributor: (data) => apiClient.post('/distributors', data).then(res => res.data),
  updateDistributor: (id, data) => apiClient.put(`/distributors/${id}`, data).then(res => res.data),
  deleteDistributor: (id) => apiClient.delete(`/distributors/${id}`).then(res => res.data),
  activateDistributor: (id) => apiClient.post(`/distributors/${id}/activate`).then(res => res.data),
  suspendDistributor: (id) => apiClient.post(`/distributors/${id}/suspend`).then(res => res.data),

  // ==================== ESTADÍSTICAS ====================
  getStats: () => apiClient.get('/stats').then(res => res.data),
  getDistributorsStats: () => apiClient.get('/distributors/stats/summary').then(res => res.data),
  getDetailedStats: () => apiClient.get('/admin/stats/detailed').then(res => res.data),
  getActivityFlow: (months = 6) => apiClient.get('/admin/stats/activity-flow', { params: { months } }).then(res => res.data),
};

export default api;