/**
 * Constantes con URLs y rutas de la API de ServiceFlow
 */
const ENDPOINTS = {
  HEALTH: '/health',
  AUTH: {
    LOGIN: '/auth/login',
    ME: '/auth/me',
    CHANGE_PASSWORD: '/auth/change-password',
  },
  USERS: {
    BASE: '/users',
    BY_ID: (id) => `/users/${id}`,
  },
  TEAMS: {
    BASE: '/teams',
    BY_ID: (id) => `/teams/${id}`,
  },
  CATEGORIES: {
    BASE: '/categories',
    BY_ID: (id) => `/categories/${id}`,
  },
  PRIORITIES: {
    BASE: '/priorities',
    BY_ID: (id) => `/priorities/${id}`,
  },
  REQUESTS: {
    BASE: '/requests/',
    BY_ID: (id) => `/requests/${id}`,
    STATUS: (id) => `/requests/${id}/status`,
    COMMENTS: (id) => `/requests/${id}/comments`,
    HISTORY: (id) => `/requests/${id}/history`,
    SLA: (id) => `/requests/${id}/sla`,
    APPROVALS: (id) => `/requests/${id}/approvals`,
    DECIDE_APPROVAL: (requestId, approvalId) => `/requests/${requestId}/approvals/${approvalId}`,
  },
  CUSTOMER: {
    REQUESTS: '/customer/requests',
    BY_ID: (id) => `/customer/requests/${id}`,
    STATUS: (id) => `/customer/requests/${id}/status`,
    PRIORITY: (id) => `/customer/requests/${id}/priority`,
    ASSIGNMENT: (id) => `/customer/requests/${id}/assignment`,
    COMMENTS: (id) => `/customer/requests/${id}/comments`,
    ATTACHMENTS: (id) => `/customer/requests/${id}/attachments`,
  },
};

module.exports = ENDPOINTS;
