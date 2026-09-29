const { test, expect } = require('@playwright/test');
const AuthClient = require('../../api/clients/AuthClient');
const RequestsClient = require('../../api/clients/RequestsClient');
const Logger = require('../../utils/logger');
const { TEST_USERS, getUniqueId } = require('../../data/testUsers');

test.describe('3. Service Agent', () => {
  let authClient;
  let requestsClient;

  let agentToken;
  let customerToken;
  let requestId;

  test.beforeAll(async ({ playwright }) => {
    const requestContext = await playwright.request.newContext();
    authClient = new AuthClient(requestContext);
    requestsClient = new RequestsClient(requestContext);

    agentToken = await authClient.getToken(TEST_USERS.AGENT.email, TEST_USERS.AGENT.password);
    customerToken = await authClient.getToken(TEST_USERS.CUSTOMER.email, TEST_USERS.CUSTOMER.password);

    const unique = getUniqueId();
    const reqRes = await requestsClient.createRequest(customerToken, {
      description: `Solicitud de soporte para módulo de Service Agent [${unique}]`,
    });
    requestId = (await reqRes.json()).id;
  });

  test('TC-AGENT-09: Cambio de estado inválido (ej. Cerrada->Nueva) → rechazado', {
    tag: ['@negativa', '@regresiva', '@media'],
  }, async () => {
    Logger.testCase('TC-AGENT-09', 'Cambio de estado inválido (ej. Cerrada->Nueva) → rechazado');

    Logger.step(1, 'Agente intenta aplicar un estado inexistente o inválido {"status": "INVALID_STATE"}');
    const res = await requestsClient.changeStatus(agentToken, requestId, {
      status: 'INVALID_STATE',
    });
    expect([400, 422]).toContain(res.status());
    const body = await res.json();
    expect(body).toHaveProperty('detail');
    Logger.pass(`Cambio de estado inválido rechazado con HTTP ${res.status()}`);
  });

  test('TC-AGENT-10: Resolver solicitud y validar timestamp de resolución', {
    tag: ['@positiva', '@regresiva', '@alta'],
  }, async () => {
    Logger.testCase('TC-AGENT-10', 'Resolver solicitud y validar timestamp de resolución');

    Logger.step(1, 'Agente transiciona la solicitud a RESOLVED');
    const res = await requestsClient.changeStatus(agentToken, requestId, {
      status: 'RESOLVED',
    });
    expect(res.status()).toBe(200);
    const data = await res.json();

    expect(data.status).toBe('RESOLVED');
    expect(data.resolved_at).not.toBeNull();
    const isoRegex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/;
    expect(data.resolved_at).toMatch(isoRegex);
    Logger.pass(`Solicitud resuelta exitosamente con timestamp resolved_at: ${data.resolved_at}`);
  });

  test('TC-AGENT-12: Agregar nota interna NO visible para el customer', {
    tag: ['@positiva', '@regresiva', '@alta'],
  }, async () => {
    Logger.testCase('TC-AGENT-12', 'Agregar nota interna NO visible para el customer');

    Logger.step(1, 'Agente agrega una nota privada marcada como is_internal: true');
    const noteRes = await requestsClient.addComment(agentToken, requestId, {
      content: 'Nota interna confidencial para el equipo de soporte técnico.',
      is_internal: true,
    });
    expect(noteRes.status()).toBe(201);
    Logger.pass('Nota interna creada por el Agente');

    Logger.step(2, 'Customer consulta los comentarios de la solicitud');
    const custCommentsRes = await requestsClient.listComments(customerToken, requestId);
    expect(custCommentsRes.status()).toBe(200);
    const customerComments = await custCommentsRes.json();

    const leaked = customerComments.some((c) => c.is_internal === true);
    expect(leaked).toBe(false);
    Logger.pass(`Aislamiento validado: Customer no ve notas internas (Total comentarios públicos: ${customerComments.length})`);
  });
});
