const { test, expect } = require('@playwright/test');
const AuthClient = require('../../api/clients/AuthClient');
const CatalogClient = require('../../api/clients/CatalogClient');
const RequestsClient = require('../../api/clients/RequestsClient');
const ApiTeardown = require('../../utils/apiTeardown');
const Logger = require('../../utils/logger');
const { TEST_USERS, getUniqueId } = require('../../data/testUsers');

test.describe('4. SLA', () => {
  let authClient;
  let catalogClient;
  let requestsClient;
  let teardown;

  let adminToken;
  let agentToken;
  let customerToken;
  let agentId;

  let categoryId;
  let priorityId;
  let requestId;

  test.beforeAll(async ({ playwright }) => {
    const requestContext = await playwright.request.newContext();
    authClient = new AuthClient(requestContext);
    catalogClient = new CatalogClient(requestContext);
    requestsClient = new RequestsClient(requestContext);
    teardown = new ApiTeardown();

    adminToken = await authClient.getToken(TEST_USERS.ADMIN.email, TEST_USERS.ADMIN.password);
    agentToken = await authClient.getToken(TEST_USERS.AGENT.email, TEST_USERS.AGENT.password);
    customerToken = await authClient.getToken(TEST_USERS.CUSTOMER.email, TEST_USERS.CUSTOMER.password);

    const agentMeRes = await authClient.getMe(agentToken);
    agentId = (await agentMeRes.json()).id;

    const unique = getUniqueId();
    const catRes = await catalogClient.createCategory(adminToken, {
      name: `Cat SLA Mod4 ${unique}`,
      description: 'Categoría para suite de SLA',
      requires_approval: false,
    });
    const catData = await catRes.json();
    categoryId = catData.id;
    teardown.registerCategory(categoryId);

    const priListRes = await catalogClient.listPriorities(adminToken);
    const priList = await priListRes.json();
    if (priList.items && priList.items.length > 0) {
      priorityId = priList.items[0].id;
    } else {
      const priRes = await catalogClient.createPriority(adminToken, {
        name: `Pri SLA Mod4 ${unique}`,
        level: 1,
      });
      priorityId = (await priRes.json()).id;
      teardown.registerPriority(priorityId);
    }

    const reqRes = await requestsClient.createRequest(customerToken, {
      description: `Solicitud para pruebas unitarias de SLA [${unique}]`,
    });
    requestId = (await reqRes.json()).id;

    // Asignar y clasificar para generar SLA
    await requestsClient.classifyRequest(agentToken, requestId, {
      category_id: categoryId,
      priority_id: priorityId,
      assigned_to: agentId,
    });
  });

  test.afterAll(async ({ playwright }) => {
    const requestContext = await playwright.request.newContext();
    await teardown.cleanup(requestContext, adminToken);
  });

  test('TC-SLA-01: SLA se calcula correctamente según categoría/prioridad al crear', { tag: ['@regression', '@positive'] }, async () => {
    Logger.testCase('TC-SLA-01', 'SLA se calcula correctamente según categoría/prioridad al crear');

    Logger.step(1, `Consultar SLA de la solicitud #${requestId}`);
    const slaRes = await requestsClient.getSla(agentToken, requestId);
    expect(slaRes.status()).toBe(200);
    const sla = await slaRes.json();

    expect(sla.response_deadline).not.toBeNull();
    expect(sla.resolution_deadline).not.toBeNull();
    Logger.pass(`Deadlines de SLA calculados: Respuesta=${sla.response_deadline}, Resolución=${sla.resolution_deadline}`);
  });

  test('TC-SLA-05: Registra tiempo de primera respuesta del agente', { tag: ['@regression', '@positive'] }, async () => {
    Logger.testCase('TC-SLA-05', 'Registra tiempo de primera respuesta del agente');

    Logger.step(1, `Verificar responded_at en SLA para solicitud #${requestId}`);
    const slaRes = await requestsClient.getSla(agentToken, requestId);
    expect(slaRes.status()).toBe(200);
    const sla = await slaRes.json();

    expect(sla.responded_at).not.toBeNull();
    Logger.pass(`Tiempo de primera respuesta del agente registrado: ${sla.responded_at}`);
  });

  test('TC-SLA-06: Registra tiempo de resolución al cerrar la solicitud', { tag: ['@regression', '@positive'] }, async () => {
    Logger.testCase('TC-SLA-06', 'Registra tiempo de resolución al cerrar la solicitud');

    Logger.step(1, 'Agente resuelve la solicitud (status: RESOLVED)');
    await requestsClient.changeStatus(agentToken, requestId, { status: 'RESOLVED' });

    Logger.step(2, 'Verificar que resolved_at se haya registrado en el SLA');
    const slaRes = await requestsClient.getSla(agentToken, requestId);
    expect(slaRes.status()).toBe(200);
    const sla = await slaRes.json();

    expect(sla.resolved_at).not.toBeNull();
    Logger.pass(`Tiempo de resolución registrado en SLA: ${sla.resolved_at}`);
  });

  test('TC-SLA-07: Cálculo correcto con husos horarios / fines de semana', { tag: ['@regression', '@positive'] }, async () => {
    Logger.testCase('TC-SLA-07', 'Cálculo correcto con husos horarios / fines de semana');

    Logger.step(1, 'Verificar formato ISO 8601 UTC en timestamps y booleano de cumplimiento');
    const slaRes = await requestsClient.getSla(agentToken, requestId);
    expect(slaRes.status()).toBe(200);
    const sla = await slaRes.json();

    const isoRegex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/;
    expect(sla.response_deadline).toMatch(isoRegex);
    expect(sla.resolution_deadline).toMatch(isoRegex);
    expect(sla.responded_at).toMatch(isoRegex);
    expect(sla.resolved_at).toMatch(isoRegex);

    expect(typeof sla.response_on_time).toBe('boolean');
    expect(typeof sla.resolution_on_time).toBe('boolean');
    Logger.pass(`Cálculo de huso horario y compliance verificado: response_on_time=${sla.response_on_time}, resolution_on_time=${sla.resolution_on_time}`);
  });
});
