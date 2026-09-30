const ENDPOINTS = require('../config/apiEndpoints');
const Logger = require('../../utils/logger');

/**
 * Cliente HTTP para el Portal de Customer (/customer/requests)
 */
class CustomerClient {
  /**
   * @param {import('@playwright/test').APIRequestContext} request
   */
  constructor(request) {
    this.request = request;
  }

  async createRequest(token, payload) {
    Logger.request('POST', ENDPOINTS.CUSTOMER.REQUESTS, payload);
    const res = await this.request.post(ENDPOINTS.CUSTOMER.REQUESTS, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      data: payload,
    });
    await Logger.logResponse(res);
    return res;
  }

  async listMyRequests(token, params = {}) {
    Logger.request('GET', ENDPOINTS.CUSTOMER.REQUESTS);
    const res = await this.request.get(ENDPOINTS.CUSTOMER.REQUESTS, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      params,
    });
    await Logger.logResponse(res);
    return res;
  }

  async getRequestDetail(token, requestId) {
    const endpoint = ENDPOINTS.CUSTOMER.BY_ID(requestId);
    Logger.request('GET', endpoint);
    const res = await this.request.get(endpoint, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    await Logger.logResponse(res);
    return res;
  }

  async getRequestStatus(token, requestId) {
    const endpoint = ENDPOINTS.CUSTOMER.STATUS(requestId);
    Logger.request('GET', endpoint);
    const res = await this.request.get(endpoint, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    await Logger.logResponse(res);
    return res;
  }

  async getRequestPriority(token, requestId) {
    const endpoint = ENDPOINTS.CUSTOMER.PRIORITY(requestId);
    Logger.request('GET', endpoint);
    const res = await this.request.get(endpoint, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    await Logger.logResponse(res);
    return res;
  }

  async getRequestAssignment(token, requestId) {
    const endpoint = ENDPOINTS.CUSTOMER.ASSIGNMENT(requestId);
    Logger.request('GET', endpoint);
    const res = await this.request.get(endpoint, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    await Logger.logResponse(res);
    return res;
  }

  async addComment(token, requestId, payload) {
    const endpoint = ENDPOINTS.CUSTOMER.COMMENTS(requestId);
    Logger.request('POST', endpoint, payload);
    const res = await this.request.post(endpoint, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      data: payload,
    });
    await Logger.logResponse(res);
    return res;
  }

  async uploadAttachment(token, requestId, file) {
    const endpoint = ENDPOINTS.CUSTOMER.ATTACHMENTS(requestId);
    Logger.request('POST [Multipart]', endpoint);
    const res = await this.request.post(endpoint, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      multipart: {
        file: {
          name: file.name,
          mimeType: file.mimeType,
          buffer: file.buffer,
        },
      },
    });
    await Logger.logResponse(res);
    return res;
  }
}

module.exports = CustomerClient;
