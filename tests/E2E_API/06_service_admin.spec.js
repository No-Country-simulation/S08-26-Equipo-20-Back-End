const { test, expect } = require('@playwright/test');
const AuthClient = require('../../api/clients/AuthClient');
const CatalogClient = require('../../api/clients/CatalogClient');
const ApiTeardown = require('../../utils/apiTeardown');
const Logger = require('../../utils/logger');
const { TEST_USERS, getUniqueId } = require('../../data/testUsers');

test.describe('6. Service Admin', () => {
  let authClient;
  let catalogClient;
  let teardown;
  let adminToken;

  test.beforeAll(async ({ playwright }) => {
    const requestContext = await playwright.request.newContext();
    authClient = new AuthClient(requestContext);
    catalogClient = new CatalogClient(requestContext);
    teardown = new ApiTeardown();

    adminToken = await authClient.getToken(TEST_USERS.ADMIN.email, TEST_USERS.ADMIN.password);
  });

  test.afterAll(async ({ playwright }) => {
    const requestContext = await playwright.request.newContext();
    await teardown.cleanup(requestContext, adminToken);
  });

  test('TC-ADM-12: Crear entidades duplicadas (nombre repetido) → validación', {
    tag: ['@negativa', '@regresiva', '@media'],
  }, async () => {
    Logger.testCase('TC-ADM-12', 'Crear entidades duplicadas (nombre repetido) → validación');

    const unique = getUniqueId();
    const catName = `Cat Duplicada Mod6 ${unique}`;

    Logger.step(1, 'Admin crea la categoría inicial');
    const firstCat = await catalogClient.createCategory(adminToken, {
      name: catName,
      description: 'Primera entidad legítima',
      requires_approval: false,
    });
    expect(firstCat.status()).toBe(201);
    const catData = await firstCat.json();
    teardown.registerCategory(catData.id);
    Logger.pass(`Categoría original creada con ID ${catData.id}`);

    Logger.step(2, 'Admin intenta crear categoría con el mismo nombre');
    const dupCat = await catalogClient.createCategory(adminToken, {
      name: catName,
      description: 'Intento duplicado',
      requires_approval: false,
    });
    expect(dupCat.status()).toBe(409);
    const body = await dupCat.json();
    expect(body.detail).toMatch(/Ya existe una categoría con ese nombre/i);
    Logger.pass(`Validación de duplicado confirmada con HTTP 409: "${body.detail}"`);

    Logger.step(3, 'Admin intenta crear prioridad con nivel existente');
    const dupPri = await catalogClient.createPriority(adminToken, {
      name: `Pri Duplicada ${unique}`,
      level: 7, // Nivel 7 existente
    });
    expect(dupPri.status()).toBe(409);
    const priBody = await dupPri.json();
    expect(priBody.detail).toMatch(/Ya existe una prioridad/i);
    Logger.pass(`Validación de conflicto confirmada para prioridades con HTTP 409: "${priBody.detail}"`);
  });
});
