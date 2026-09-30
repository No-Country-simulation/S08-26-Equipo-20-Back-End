const ENDPOINTS = require('../config/apiEndpoints');
const Logger = require('../../utils/logger');

/**
 * Cliente HTTP para gestión de Solicitudes (Agentes y Administradores)
 */
class RequestsClient {
  /**
   * @param {import('@playwright/test').APIRequestContext} request
   */
  constructor(request) {
    this.request = request;
  }

  async createRequest(token, payload) {
    Logger.request('POST', ENDPOINTS.REQUESTS.BASE, payload);
    const res = await this.request.post(ENDPOINTS.REQUESTS.BASE, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      data: payload,
    });
    await Logger.logResponse(res);
    return res;
  }

  async listRequests(token) {
    Logger.request('GET', ENDPOINTS.REQUESTS.BASE);
    const res = await this.request.get(ENDPOINTS.REQUESTS.BASE, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    await Logger.logResponse(res);
    return res;
  }

  async getRequest(token, requestId) {
    const endpoint = ENDPOINTS.REQUESTS.BY_ID(requestId);
    Logger.request('GET', endpoint);
    const res = await this.request.get(endpoint, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    await Logger.logResponse(res);
    return res;
  }

  async classifyRequest(token, requestId, payload) {
    const endpoint = ENDPOINTS.REQUESTS.BY_ID(requestId);
    Logger.request('PATCH', endpoint, payload);
    const res = await this.request.patch(endpoint, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      data: payload,
    });
    await Logger.logResponse(res);
    return res;
  }

  async changeStatus(token, requestId, payload) {
    const endpoint = ENDPOINTS.REQUESTS.STATUS(requestId);
    Logger.request('PATCH', endpoint, payload);
    const res = await this.request.patch(endpoint, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      data: payload,
    });
    await Logger.logResponse(res);
    return res;
  }

  async addComment(token, requestId, payload) {
    const endpoint = ENDPOINTS.REQUESTS.COMMENTS(requestId);
    Logger.request('POST', endpoint, payload);
    const res = await this.request.post(endpoint, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      data: payload,
    });
    await Logger.logResponse(res);
    return res;
  }

  async listComments(token, requestId) {
    const endpoint = ENDPOINTS.REQUESTS.COMMENTS(requestId);
    Logger.request('GET', endpoint);
    const res = await this.request.get(endpoint, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    await Logger.logResponse(res);
    return res;
  }

  async listHistory(token, requestId) {
    const endpoint = ENDPOINTS.REQUESTS.HISTORY(requestId);
    Logger.request('GET', endpoint);
    const res = await this.request.get(endpoint, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    await Logger.logResponse(res);
    return res;
  }

  async getSla(token, requestId) {
    const endpoint = ENDPOINTS.REQUESTS.SLA(requestId);
    Logger.request('GET', endpoint);
    const res = await this.request.get(endpoint, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    await Logger.logResponse(res);
    return res;
  }

  async upsertSla(token, requestId, payload) {
    const endpoint = ENDPOINTS.REQUESTS.SLA(requestId);
    Logger.request('PUT', endpoint, payload);
    const res = await this.request.put(endpoint, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      data: payload,
    });
    await Logger.logResponse(res);
    return res;
  }

  async listApprovals(token, requestId) {
    const endpoint = ENDPOINTS.REQUESTS.APPROVALS(requestId);
    Logger.request('GET', endpoint);
    const res = await this.request.get(endpoint, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    await Logger.logResponse(res);
    return res;
  }

  async decideApproval(token, requestId, approvalId, payload) {
    const endpoint = ENDPOINTS.REQUESTS.DECIDE_APPROVAL(requestId, approvalId);
    Logger.request('PATCH', endpoint, payload);
    const res = await this.request.patch(endpoint, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      data: payload,
    });
    await Logger.logResponse(res);
    return res;
  }
}

module.exports = RequestsClient;
