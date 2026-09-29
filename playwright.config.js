// @ts-check
const { defineConfig } = require('@playwright/test');

/**
 * Configuración global para Playwright API Testing en ServiceFlow
 */
module.exports = defineConfig({
  testDir: './tests',
  fullyParallel: false,
  workers: 1, // Ejecución secuencial para no generar carreras en base de datos
  timeout: 30000,
  retries: 0,
  reporter: [
    ['list'],
    ['html', { open: 'never', outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'test-results.json' }],
    ['allure-playwright', { outputFolder: 'allure-results' }]
  ],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:8000',
    extraHTTPHeaders: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
    ignoreHTTPSErrors: true,
  },
});
