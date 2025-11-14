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
  // ==================== AUTENTICACIÓN - CORREGIDO ====================
  login: (username, password) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    return apiClient.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
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

  // ==================== INVENTORY - VENDEDORES ====================
  getVendedores: (params) => apiClient.get('/v1/inventory/vendedores', { params }).then(res => res.data),
  getVendedor: (id) => apiClient.get(`/v1/inventory/vendedores/${id}`).then(res => res.data),
  createVendedor: (data) => apiClient.post('/v1/inventory/vendedores', data).then(res => res.data),
  updateVendedor: (id, data) => apiClient.put(`/v1/inventory/vendedores/${id}`, data).then(res => res.data),
  deleteVendedor: (id) => apiClient.delete(`/v1/inventory/vendedores/${id}`).then(res => res.data),

  // ==================== INVENTORY - PRODUCTOS ====================
  getProductos: (params) => apiClient.get('/v1/inventory/productos', { params }).then(res => res.data),
  getProducto: (id) => apiClient.get(`/v1/inventory/productos/${id}`).then(res => res.data),
  createProducto: (data) => apiClient.post('/v1/inventory/productos', data).then(res => res.data),
  updateProducto: (id, data) => apiClient.put(`/v1/inventory/productos/${id}`, data).then(res => res.data),
  deleteProducto: (id) => apiClient.delete(`/v1/inventory/productos/${id}`).then(res => res.data),

  // ==================== INVENTORY - STOCK ====================
  getStock: (params) => apiClient.get('/v1/inventory/stock', { params }).then(res => res.data),
  getStockVendedor: (vendedorId) => apiClient.get(`/v1/inventory/stock/vendedor/${vendedorId}`).then(res => res.data),
  asignarStock: (data) => apiClient.post('/v1/inventory/stock/asignar', data).then(res => res.data),
  updateStock: (id, data) => apiClient.put(`/v1/inventory/stock/${id}`, data).then(res => res.data),

  // ==================== INVENTORY - VENTAS ====================
  getVentas: (params) => apiClient.get('/v1/inventory/ventas', { params }).then(res => res.data),
  getVenta: (id) => apiClient.get(`/v1/inventory/ventas/${id}`).then(res => res.data),
  createVenta: (data) => apiClient.post('/v1/inventory/ventas', data).then(res => res.data),
  updateVenta: (id, data) => apiClient.put(`/v1/inventory/ventas/${id}`, data).then(res => res.data),
  deleteVenta: (id) => apiClient.delete(`/v1/inventory/ventas/${id}`).then(res => res.data),

  // ==================== INVENTORY - AJUSTES ====================
  getAjustes: (params) => apiClient.get('/v1/inventory/ajustes', { params }).then(res => res.data),
  createAjuste: (data) => apiClient.post('/v1/inventory/ajustes', data).then(res => res.data),

  // ==================== INVENTORY - ASIGNACIONES ====================
  getAsignaciones: (params) => apiClient.get('/v1/inventory/asignaciones', { params }).then(res => res.data),

  // ==================== INVENTORY - ESTADÍSTICAS ====================
  getEstadisticasInventario: () => apiClient.get('/v1/inventory/estadisticas/general').then(res => res.data),
  getEstadisticasVendedor: (id) => apiClient.get(`/v1/inventory/estadisticas/vendedor/${id}`).then(res => res.data),
  getEstadisticasProducto: (id) => apiClient.get(`/v1/inventory/estadisticas/producto/${id}`).then(res => res.data),
};

export default api;