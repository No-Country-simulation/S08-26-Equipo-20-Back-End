const ENDPOINTS = require('../config/apiEndpoints');
const Logger = require('../../utils/logger');

/**
 * Cliente HTTP para módulo de Autenticación
 */
class AuthClient {
  /**
   * @param {import('@playwright/test').APIRequestContext} request
   */
  constructor(request) {
    this.request = request;
  }

  async login(email, password) {
    Logger.request('POST', ENDPOINTS.AUTH.LOGIN, { email, password: '***' });
    const res = await this.request.post(ENDPOINTS.AUTH.LOGIN, {
      data: { email, password },
    });
    await Logger.logResponse(res);
    return res;
  }

  async getToken(email, password) {
    const response = await this.login(email, password);
    if (!response.ok()) {
      throw new Error(`Error en login para ${email}: ${response.status()} ${await response.text()}`);
    }
    const body = await response.json();
    return body.access_token;
  }

  async getMe(token) {
    Logger.request('GET', ENDPOINTS.AUTH.ME);
    const res = await this.request.get(ENDPOINTS.AUTH.ME, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    await Logger.logResponse(res);
    return res;
  }

  async changePassword(token, currentPassword, newPassword) {
    Logger.request('POST', ENDPOINTS.AUTH.CHANGE_PASSWORD);
    const res = await this.request.post(ENDPOINTS.AUTH.CHANGE_PASSWORD, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      data: {
        current_password: currentPassword,
        new_password: newPassword,
      },
    });
    await Logger.logResponse(res);
    return res;
  }
}

module.exports = AuthClient;
