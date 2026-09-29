const ENDPOINTS = require('../config/apiEndpoints');
const Logger = require('../../utils/logger');

class CatalogClient {
  constructor(request) {
    this.request = request;
  }

  async createCategory(token, payload) {
    Logger.request('POST', ENDPOINTS.CATEGORIES.BASE, payload);
    const res = await this.request.post(ENDPOINTS.CATEGORIES.BASE, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      data: payload,
    });
    await Logger.logResponse(res);
    return res;
  }

  async listCategories(token, params = {}) {
    Logger.request('GET', ENDPOINTS.CATEGORIES.BASE);
    const res = await this.request.get(ENDPOINTS.CATEGORIES.BASE, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      params,
    });
    await Logger.logResponse(res);
    return res;
  }

  async getCategory(token, categoryId) {
    const endpoint = ENDPOINTS.CATEGORIES.BY_ID(categoryId);
    Logger.request('GET', endpoint);
    const res = await this.request.get(endpoint, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    await Logger.logResponse(res);
    return res;
  }

  async deleteCategory(token, categoryId) {
    const endpoint = ENDPOINTS.CATEGORIES.BY_ID(categoryId);
    Logger.request('DELETE', endpoint);
    const res = await this.request.delete(endpoint, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    await Logger.logResponse(res);
    return res;
  }

  async createPriority(token, payload) {
    Logger.request('POST', ENDPOINTS.PRIORITIES.BASE, payload);
    const res = await this.request.post(ENDPOINTS.PRIORITIES.BASE, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      data: payload,
    });
    await Logger.logResponse(res);
    return res;
  }

  async listPriorities(token, params = {}) {
    Logger.request('GET', ENDPOINTS.PRIORITIES.BASE);
    const res = await this.request.get(ENDPOINTS.PRIORITIES.BASE, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      params,
    });
    await Logger.logResponse(res);
    return res;
  }

  async deletePriority(token, priorityId) {
    const endpoint = ENDPOINTS.PRIORITIES.BY_ID(priorityId);
    Logger.request('DELETE', endpoint);
    const res = await this.request.delete(endpoint, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    await Logger.logResponse(res);
    return res;
  }

  async createTeam(token, payload) {
    Logger.request('POST', ENDPOINTS.TEAMS.BASE, payload);
    const res = await this.request.post(ENDPOINTS.TEAMS.BASE, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      data: payload,
    });
    await Logger.logResponse(res);
    return res;
  }

  async deleteTeam(token, teamId) {
    const endpoint = ENDPOINTS.TEAMS.BY_ID(teamId);
    Logger.request('DELETE', endpoint);
    const res = await this.request.delete(endpoint, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    await Logger.logResponse(res);
    return res;
  }
}

module.exports = CatalogClient;
