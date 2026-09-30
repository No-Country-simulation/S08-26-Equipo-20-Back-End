const { test, expect } = require('@playwright/test');
const Logger = require('../../utils/logger');
const ENDPOINTS = require('../../api/config/apiEndpoints');

test.describe('9. Smoke (pre-build)', () => {
  test('SM-04: Health check: todos los servicios levantan correctamente', { tag: ['@smoke', '@regression', '@positive'] }, async ({ request }) => {
    Logger.testCase('SM-04', 'Health check: todos los servicios levantan correctamente');

    Logger.step(1, 'Consultar endpoint GET /health para verificar estado del servidor');
    const res = await request.get(ENDPOINTS.HEALTH);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body.status).toBe('ok');
    Logger.pass(`Health check de pre-build exitoso: ${JSON.stringify(body)} (HTTP 200)`);
  });
});
