const { test, expect } = require('@playwright/test');
const AuthClient = require('../../api/clients/AuthClient');
const UsersClient = require('../../api/clients/UsersClient');
const CustomerClient = require('../../api/clients/CustomerClient');
const RequestsClient = require('../../api/clients/RequestsClient');
const ApiTeardown = require('../../utils/apiTeardown');
const Logger = require('../../utils/logger');
const {
  TEST_USERS,
  getUniqueId,
  createInvalidSignedToken,
} = require('../../data/testUsers');

test.describe('7. Seguridad', () => {
  let authClient;
  let usersClient;
  let customerClient;
  let requestsClient;
  let teardown;

  let adminToken;
  let customerAToken;
  let customerBToken;
  let customerBId;
  let requestAId;

  test.beforeAll(async ({ playwright }) => {
    const requestContext = await playwright.request.newContext();
    authClient = new AuthClient(requestContext);
    usersClient = new UsersClient(requestContext);
    customerClient = new CustomerClient(requestContext);
    requestsClient = new RequestsClient(requestContext);
    teardown = new ApiTeardown();

    adminToken = await authClient.getToken(TEST_USERS.ADMIN.email, TEST_USERS.ADMIN.password);
    customerAToken = await authClient.getToken(TEST_USERS.CUSTOMER.email, TEST_USERS.CUSTOMER.password);

    const unique = getUniqueId();
    const customerBEmail = `sec_cust_${unique}@test.com`;
    const customerBPassword = 'Password123!';

    const createRes = await usersClient.createUser(adminToken, {
      name: `Customer B Security ${unique}`,
      email: customerBEmail,
      password: customerBPassword,
      role_id: 3,
    });
    const createData = await createRes.json();
    customerBId = createData.user.id;
    teardown.registerUser(customerBId);

    customerBToken = await authClient.getToken(customerBEmail, customerBPassword);

    const reqRes = await requestsClient.createRequest(customerAToken, {
      description: `Solicitud de Customer A para auditoría de seguridad [${unique}]`,
    });
    requestAId = (await reqRes.json()).id;
  });

  test.afterAll(async ({ playwright }) => {
    const requestContext = await playwright.request.newContext();
    await teardown.cleanup(requestContext, adminToken);
  });

  test('TC-SEC-01: IDOR: customer no ve solicitudes ajenas', {
    tag: ['@negativa', '@regresiva', '@alta'],
  }, async () => {
    Logger.testCase('TC-SEC-01', 'IDOR: customer no ve solicitudes ajenas');

    Logger.step(1, `Customer B intenta acceder a solicitud #${requestAId} perteneciente a Customer A`);
    const res = await customerClient.getRequestDetail(customerBToken, requestAId);
    expect([403, 404]).toContain(res.status());
    const body = await res.json();
    expect(body.detail).toMatch(/Acceso denegado|pertenece a otro usuario/i);
    Logger.pass(`IDOR bloqueado: Servidor retornó HTTP ${res.status()} "${body.detail}"`);
  });

  test('TC-SEC-02: IDOR: customer no accede a comentarios/archivos ajenos', {
    tag: ['@negativa', '@regresiva', '@alta'],
  }, async () => {
    Logger.testCase('TC-SEC-02', 'IDOR: customer no accede a comentarios/archivos ajenos');

    Logger.step(1, `Customer B intenta añadir comentario a solicitud ajena #${requestAId}`);
    const res = await customerClient.addComment(customerBToken, requestAId, {
      content: 'Intento de comentario no autorizado',
    });
    expect([403, 404]).toContain(res.status());
    const body = await res.json();
    expect(body.detail).toMatch(/Acceso denegado|pertenece a otro usuario/i);
    Logger.pass(`Intrusión a comentarios ajenos rechazada con HTTP ${res.status()}`);
  });

  test('TC-SEC-03: Bypass de UI: endpoint restringido llamado con rol inferior vía API', {
    tag: ['@negativa', '@regresiva', '@alta'],
  }, async () => {
    Logger.testCase('TC-SEC-03', 'Bypass de UI: endpoint restringido llamado con rol inferior vía API');

    Logger.step(1, 'Customer llama a endpoint reservado para Agente/Admin (PATCH /requests/{id})');
    const res = await requestsClient.classifyRequest(customerAToken, requestAId, {
      category_id: 1,
    });
    expect(res.status()).toBe(403);
    const body = await res.json();
    expect(body.detail).toMatch(/permisos/i);
    Logger.pass(`Bypass de interfaz bloqueado a nivel de API con HTTP 403: "${body.detail}"`);
  });

  test('TC-SEC-04: JWT alterado (rol modificado sin re-firmar) → rechazado', {
    tag: ['@negativa', '@regresiva', '@alta'],
  }, async () => {
    Logger.testCase('TC-SEC-04', 'JWT alterado (rol modificado sin re-firmar) → rechazado');

    Logger.step(1, 'Enviar token con firma falsa o manipulada a endpoint protegido');
    const fakeToken = createInvalidSignedToken();
    const res = await authClient.getMe(fakeToken);
    expect([401, 403]).toContain(res.status());
    Logger.pass(`Token con firma alterada rechazado con HTTP ${res.status()}`);
  });

  test('TC-SEC-05: Escalamiento por parámetro oculto ("role":"admin" en creación de usuario)', {
    tag: ['@negativa', '@regresiva', '@alta'],
  }, async () => {
    Logger.testCase('TC-SEC-05', 'Escalamiento por parámetro oculto ("role":"admin" en creación de usuario)');

    const unique = getUniqueId();

    Logger.step(1, 'Customer intenta invocar POST /users inyectando {"role": "admin"}');
    const unauthRes = await usersClient.createUser(customerAToken, {
      name: `Hacker ${unique}`,
      email: `hacker_${unique}@test.com`,
      role: 'admin',
      role_id: 1,
    });
    expect(unauthRes.status()).toBe(403);
    Logger.pass('Escalamiento no autorizado bloqueado con HTTP 403');

    Logger.step(2, 'Inyección de parámetro {"role": "admin"} sin role_id obligatorio');
    const badParamRes = await usersClient.createUser(adminToken, {
      name: `Attacker ${unique}`,
      email: `attack_${unique}@test.com`,
      role: 'admin',
    });
    expect(badParamRes.status()).toBe(422);
    const body = await badParamRes.json();
    expect(body.detail[0].loc).toContain('role_id');
    Logger.pass('Validación de esquema exige role_id tipado y rechaza inyección oculta con HTTP 422');
  });
});
