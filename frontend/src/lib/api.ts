/**
 * Typed API client — wraps axios with auth token injection.
 * All calls go through this client so token refresh can be added centrally.
 */

import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: `${API_BASE}/api`,
  headers: { 'Content-Type': 'application/json' },
});

// Inject JWT token from localStorage on every request
apiClient.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('fieldops_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
  }
  return config;
});

// On 401 redirect to login
apiClient.interceptors.response.use(
  (r) => r,
  (error) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      const path = window.location.pathname;
      if (path !== '/login') {
        localStorage.removeItem('fieldops_token');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// ── Auth ────────────────────────────────────────────────────────────────────
export const authApi = {
  login: (username: string, password: string) => {
    const form = new URLSearchParams();
    form.append('username', username);
    form.append('password', password);
    return apiClient.post<{ access_token: string; token_type: string }>('/auth/token', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
  },
  me: () => apiClient.get('/auth/me'),
};

// ── Dashboard ────────────────────────────────────────────────────────────────
export const dashboardApi = {
  metrics: () => apiClient.get('/dashboard'),
};

// ── Customers ────────────────────────────────────────────────────────────────
export const customersApi = {
  list: (params?: Record<string, unknown>) => apiClient.get('/customers', { params }),
  get: (id: number) => apiClient.get(`/customers/${id}`),
  create: (data: Record<string, unknown>) => apiClient.post('/customers', data),
  update: (id: number, data: Record<string, unknown>) => apiClient.patch(`/customers/${id}`, data),
  archive: (id: number) => apiClient.delete(`/customers/${id}`),
};

// ── Sites ────────────────────────────────────────────────────────────────────
export const sitesApi = {
  list: (params?: Record<string, unknown>) => apiClient.get('/sites', { params }),
  get: (id: number) => apiClient.get(`/sites/${id}`),
  create: (data: Record<string, unknown>) => apiClient.post('/sites', data),
  update: (id: number, data: Record<string, unknown>) => apiClient.patch(`/sites/${id}`, data),
  delete: (id: number) => apiClient.delete(`/sites/${id}`),
};

// ── Assets ───────────────────────────────────────────────────────────────────
export const assetsApi = {
  list: (params?: Record<string, unknown>) => apiClient.get('/assets', { params }),
  get: (id: number) => apiClient.get(`/assets/${id}`),
  create: (data: Record<string, unknown>) => apiClient.post('/assets', data),
  update: (id: number, data: Record<string, unknown>) => apiClient.patch(`/assets/${id}`, data),
  archive: (id: number) => apiClient.delete(`/assets/${id}`),
};

// ── Tickets ──────────────────────────────────────────────────────────────────
export const ticketsApi = {
  list: (params?: Record<string, unknown>) => apiClient.get('/tickets', { params }),
  get: (id: number) => apiClient.get(`/tickets/${id}`),
  create: (data: Record<string, unknown>) => apiClient.post('/tickets', data),
  update: (id: number, data: Record<string, unknown>) => apiClient.patch(`/tickets/${id}`, data),
  events: (id: number) => apiClient.get(`/tickets/${id}/events`),
  addNote: (id: number, data: { event_type: string; detail: string }) =>
    apiClient.post(`/tickets/${id}/events`, data),
};

// ── Technicians ──────────────────────────────────────────────────────────────
export const techniciansApi = {
  list: (params?: Record<string, unknown>) => apiClient.get('/technicians', { params }),
  get: (id: number) => apiClient.get(`/technicians/${id}`),
  create: (data: Record<string, unknown>) => apiClient.post('/technicians', data),
  update: (id: number, data: Record<string, unknown>) => apiClient.patch(`/technicians/${id}`, data),
};

// ── Contracts ────────────────────────────────────────────────────────────────
export const contractsApi = {
  list: (params?: Record<string, unknown>) => apiClient.get('/contracts', { params }),
  get: (id: number) => apiClient.get(`/contracts/${id}`),
  create: (data: Record<string, unknown>) => apiClient.post('/contracts', data),
  update: (id: number, data: Record<string, unknown>) => apiClient.patch(`/contracts/${id}`, data),
};

// ── Maintenance ──────────────────────────────────────────────────────────────
export const maintenanceApi = {
  list: (params?: Record<string, unknown>) => apiClient.get('/maintenance', { params }),
  get: (id: number) => apiClient.get(`/maintenance/${id}`),
  create: (data: Record<string, unknown>) => apiClient.post('/maintenance', data),
  update: (id: number, data: Record<string, unknown>) => apiClient.patch(`/maintenance/${id}`, data),
};

// ── Knowledge Base ────────────────────────────────────────────────────────────
export const knowledgeApi = {
  list: () => apiClient.get('/knowledge/documents'),
  get: (id: number) => apiClient.get(`/knowledge/documents/${id}`),
  upload: (formData: FormData) =>
    apiClient.post('/knowledge/documents', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  delete: (id: number) => apiClient.delete(`/knowledge/documents/${id}`),
};

// ── AI Assistant ─────────────────────────────────────────────────────────────
export const assistantApi = {
  query: (question: string, context?: string) =>
    apiClient.post('/assistant', { question, context }),
};

// ── Reports ──────────────────────────────────────────────────────────────────
export const reportsApi = {
  tickets: () => apiClient.get('/reports/tickets'),
  assets: () => apiClient.get('/reports/assets'),
  serviceReport: (ticketId: number) => apiClient.get(`/reports/tickets/${ticketId}/service-report`),
};
