const { test, expect } = require('@playwright/test');
const AuthClient = require('../../api/clients/AuthClient');
const UsersClient = require('../../api/clients/UsersClient');
const CustomerClient = require('../../api/clients/CustomerClient');
const RequestsClient = require('../../api/clients/RequestsClient');
const ApiTeardown = require('../../utils/apiTeardown');
const Logger = require('../../utils/logger');
const { TEST_USERS, getUniqueId } = require('../../data/testUsers');

test.describe('2. Customer: Solicitudes', () => {
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
    const customerBEmail = `cust_b_${unique}@test.com`;
    const customerBPassword = 'Password123!';

    const createRes = await usersClient.createUser(adminToken, {
      name: `Customer B ${unique}`,
      email: customerBEmail,
      password: customerBPassword,
      role_id: 3,
    });
    const createData = await createRes.json();
    customerBId = createData.user.id;
    teardown.registerUser(customerBId);

    customerBToken = await authClient.getToken(customerBEmail, customerBPassword);

    const reqRes = await requestsClient.createRequest(customerAToken, {
      description: `Solicitud de Customer A para prueba de Customer Portal [${unique}]`,
    });
    requestAId = (await reqRes.json()).id;
  });

  test.afterAll(async ({ playwright }) => {
    const requestContext = await playwright.request.newContext();
    await teardown.cleanup(requestContext, adminToken);
  });

  test('TC-CUST-05: Ver detalle de solicitud de otro customer → 403/404 (IDOR)', {
    tag: ['@negativa', '@regresiva', '@alta'],
  }, async () => {
    Logger.testCase('TC-CUST-05', 'Ver detalle de solicitud de otro customer → 403/404 (IDOR)');

    Logger.step(1, `Customer B intenta ver el detalle de solicitud #${requestAId} creada por Customer A`);
    const res = await customerClient.getRequestDetail(customerBToken, requestAId);
    expect([403, 404]).toContain(res.status());
    const body = await res.json();
    expect(body.detail).toMatch(/Acceso denegado|pertenece a otro usuario/i);
    Logger.pass(`Acceso denegado a solicitud ajena con HTTP ${res.status()}: "${body.detail}"`);
  });

  test('TC-CUST-10: Agregar comentario a solicitud de otro customer → rechazado', {
    tag: ['@negativa', '@regresiva', '@alta'],
  }, async () => {
    Logger.testCase('TC-CUST-10', 'Agregar comentario a solicitud de otro customer → rechazado');

    Logger.step(1, `Customer B intenta publicar comentario en solicitud #${requestAId} de Customer A`);
    const res = await customerClient.addComment(customerBToken, requestAId, {
      content: 'Comentario no autorizado de otro usuario',
    });
    expect([403, 404]).toContain(res.status());
    const body = await res.json();
    expect(body.detail).toMatch(/Acceso denegado|pertenece a otro usuario/i);
    Logger.pass(`Publicación de comentario rechazada con HTTP ${res.status()}: "${body.detail}"`);
  });
});
