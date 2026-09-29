const { test, expect } = require('@playwright/test');
const AuthClient = require('../../api/clients/AuthClient');
const CatalogClient = require('../../api/clients/CatalogClient');
const RequestsClient = require('../../api/clients/RequestsClient');
const ApiTeardown = require('../../utils/apiTeardown');
const Logger = require('../../utils/logger');
const { TEST_USERS, getUniqueId } = require('../../data/testUsers');

test.describe('5. Aprobaciones', () => {
  let authClient;
  let catalogClient;
  let requestsClient;
  let teardown;

  let adminToken;
  let agentToken;
  let customerToken;

  let categoryWithApprovalId;
  let categoryWithoutApprovalId;
  let requestWithApprovalId;
  let requestWithoutApprovalId;
  let generatedApprovalId;

  test.beforeAll(async ({ playwright }) => {
    const requestContext = await playwright.request.newContext();
    authClient = new AuthClient(requestContext);
    catalogClient = new CatalogClient(requestContext);
    requestsClient = new RequestsClient(requestContext);
    teardown = new ApiTeardown();

    adminToken = await authClient.getToken(TEST_USERS.ADMIN.email, TEST_USERS.ADMIN.password);
    agentToken = await authClient.getToken(TEST_USERS.AGENT.email, TEST_USERS.AGENT.password);
    customerToken = await authClient.getToken(TEST_USERS.CUSTOMER.email, TEST_USERS.CUSTOMER.password);

    const unique = getUniqueId();

    const cat1Res = await catalogClient.createCategory(adminToken, {
      name: `Cat Con Aprobación Mod5 ${unique}`,
      description: 'Requiere autorización formal',
      requires_approval: true,
    });
    categoryWithApprovalId = (await cat1Res.json()).id;
    teardown.registerCategory(categoryWithApprovalId);

    const cat2Res = await catalogClient.createCategory(adminToken, {
      name: `Cat Sin Aprobación Mod5 ${unique}`,
      description: 'Flujo sin aprobación',
      requires_approval: false,
    });
    categoryWithoutApprovalId = (await cat2Res.json()).id;
    teardown.registerCategory(categoryWithoutApprovalId);

    const r1 = await requestsClient.createRequest(customerToken, {
      description: `Solicitud con aprobación requerida [${unique}]`,
    });
    requestWithApprovalId = (await r1.json()).id;

    const r2 = await requestsClient.createRequest(customerToken, {
      description: `Solicitud estándar directa [${unique}]`,
    });
    requestWithoutApprovalId = (await r2.json()).id;
  });

  test.afterAll(async ({ playwright }) => {
    const requestContext = await playwright.request.newContext();
    await teardown.cleanup(requestContext, adminToken);
  });

  test('TC-APR-01: Categoría "Requiere Aprobación=true" dispara el flujo automáticamente', {
    tag: ['@positiva', '@regresiva', '@alta'],
  }, async () => {
    Logger.testCase('TC-APR-01', 'Categoría "Requiere Aprobación=true" dispara el flujo automáticamente');

    Logger.step(1, `Clasificar solicitud #${requestWithApprovalId} con categoría que exige aprobación`);
    await requestsClient.classifyRequest(agentToken, requestWithApprovalId, {
      category_id: categoryWithApprovalId,
    });

    Logger.step(2, 'Verificar que la aprobación fue autogenerada');
    const apprRes = await requestsClient.listApprovals(agentToken, requestWithApprovalId);
    expect(apprRes.status()).toBe(200);
    const approvals = await apprRes.json();

    expect(approvals.length).toBeGreaterThan(0);
    generatedApprovalId = approvals[0].id;
    expect(approvals[0].status).toBe('PENDING');
    Logger.pass(`Aprobación #${generatedApprovalId} disparada automáticamente en estado: ${approvals[0].status}`);
  });

  test('TC-APR-02: Categoría "Requiere Aprobación=false" NO dispara el flujo', {
    tag: ['@positiva', '@regresiva', '@alta'],
  }, async () => {
    Logger.testCase('TC-APR-02', 'Categoría "Requiere Aprobación=false" NO dispara el flujo');

    Logger.step(1, `Clasificar solicitud #${requestWithoutApprovalId} con categoría que no exige aprobación`);
    await requestsClient.classifyRequest(agentToken, requestWithoutApprovalId, {
      category_id: categoryWithoutApprovalId,
    });

    Logger.step(2, 'Verificar que la lista de aprobaciones permanece vacía');
    const apprRes = await requestsClient.listApprovals(agentToken, requestWithoutApprovalId);
    expect(apprRes.status()).toBe(200);
    const approvals = await apprRes.json();
    expect(approvals.length).toBe(0);
    Logger.pass('Validado: No se generó flujo de aprobación');
  });

  test('TC-APR-07: Trazabilidad: quién aprobó/rechazó y cuándo', {
    tag: ['@positiva', '@regresiva', '@alta'],
  }, async () => {
    Logger.testCase('TC-APR-07', 'Trazabilidad: quién aprobó/rechazó y cuándo');

    Logger.step(1, `ADMIN aprueba formalmente la aprobación #${generatedApprovalId}`);
    const decideRes = await requestsClient.decideApproval(
      adminToken,
      requestWithApprovalId,
      generatedApprovalId,
      { status: 'APPROVED', comment: 'Aprobación auditada por dirección técnica' }
    );
    expect(decideRes.status()).toBe(200);
    const decideData = await decideRes.json();

    expect(decideData.status).toBe('APPROVED');
    expect(decideData.decided_at).not.toBeNull();
    expect(decideData.approver.email).toBeTruthy();
    Logger.pass(`Aprobación registrada con timestamp: ${decideData.decided_at} por ${decideData.approver.email}`);

    Logger.step(2, 'Consultar historial de auditoría de la solicitud');
    const histRes = await requestsClient.listHistory(agentToken, requestWithApprovalId);
    expect(histRes.status()).toBe(200);
    const history = await histRes.json();
    expect(history.length).toBeGreaterThan(0);
    Logger.pass(`Trazabilidad confirmada con ${history.length} evento(s) en historial`);
  });

  test('TC-APR-08: Customer no puede auto-aprobar su propia solicitud', {
    tag: ['@negativa', '@regresiva', '@alta'],
  }, async () => {
    Logger.testCase('TC-APR-08', 'Customer no puede auto-aprobar su propia solicitud');

    Logger.step(1, `Customer intenta decidir aprobación #${generatedApprovalId} en solicitud #${requestWithApprovalId}`);
    const res = await requestsClient.decideApproval(
      customerToken,
      requestWithApprovalId,
      generatedApprovalId,
      { status: 'APPROVED', comment: 'Intento de auto-aprobación' }
    );
    expect(res.status()).toBe(403);
    const body = await res.json();
    expect(body.detail).toMatch(/permisos/i);
    Logger.pass(`Intento de auto-aprobación rechazado con HTTP 403: "${body.detail}"`);
  });
});
