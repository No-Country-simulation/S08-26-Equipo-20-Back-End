const ENDPOINTS = require('../config/apiEndpoints');
const Logger = require('../../utils/logger');

class UsersClient {
  constructor(request) {
    this.request = request;
  }

  async createUser(token, payload) {
    Logger.request('POST', ENDPOINTS.USERS.BASE, payload);
    const res = await this.request.post(ENDPOINTS.USERS.BASE, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      data: payload,
    });
    await Logger.logResponse(res);
    return res;
  }

  async listUsers(token, params = {}) {
    Logger.request('GET', ENDPOINTS.USERS.BASE);
    const res = await this.request.get(ENDPOINTS.USERS.BASE, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      params,
    });
    await Logger.logResponse(res);
    return res;
  }

  async getUser(token, userId) {
    const endpoint = ENDPOINTS.USERS.BY_ID(userId);
    Logger.request('GET', endpoint);
    const res = await this.request.get(endpoint, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    await Logger.logResponse(res);
    return res;
  }

  async updateUser(token, userId, payload) {
    const endpoint = ENDPOINTS.USERS.BY_ID(userId);
    Logger.request('PATCH', endpoint, payload);
    const res = await this.request.patch(endpoint, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      data: payload,
    });
    await Logger.logResponse(res);
    return res;
  }

  async deleteUser(token, userId) {
    const endpoint = ENDPOINTS.USERS.BY_ID(userId);
    Logger.request('DELETE', endpoint);
    const res = await this.request.delete(endpoint, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    await Logger.logResponse(res);
    return res;
  }
}

module.exports = UsersClient;
