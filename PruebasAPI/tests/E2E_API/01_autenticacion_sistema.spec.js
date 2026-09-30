const { test, expect } = require('@playwright/test');
const AuthClient = require('../../api/clients/AuthClient');
const UsersClient = require('../../api/clients/UsersClient');
const CatalogClient = require('../../api/clients/CatalogClient');
const RequestsClient = require('../../api/clients/RequestsClient');
const Logger = require('../../utils/logger');
const { validateSchema } = require('../../utils/schemaValidator');
const { loginResponseSchema, userMeResponseSchema } = require('../../schemas/auth.schema');
const {
  TEST_USERS,
  createExpiredToken,
  createManipulatedToken,
} = require('../../data/testUsers');
const ENDPOINTS = require('../../api/config/apiEndpoints');

test.describe('1. Autenticación y Sistema', () => {
  let authClient;
  let usersClient;
  let catalogClient;
  let requestsClient;

  let adminToken;
  let agentToken;
  let customerToken;

  test.beforeAll(async ({ playwright }) => {
    const requestContext = await playwright.request.newContext();
    authClient = new AuthClient(requestContext);
    usersClient = new UsersClient(requestContext);
    catalogClient = new CatalogClient(requestContext);
    requestsClient = new RequestsClient(requestContext);

    adminToken = await authClient.getToken(TEST_USERS.ADMIN.email, TEST_USERS.ADMIN.password);
    agentToken = await authClient.getToken(TEST_USERS.AGENT.email, TEST_USERS.AGENT.password);
    customerToken = await authClient.getToken(TEST_USERS.CUSTOMER.email, TEST_USERS.CUSTOMER.password);
  });

  test('TC-AUTH-04: Token Bearer token generado contiene el rol correcto', { tag: ['@smoke', '@regression', '@positive'] }, async () => {
    Logger.testCase('TC-AUTH-04', 'Token Bearer token generado contiene el rol correcto');

    Logger.step(1, 'Verificar rol ADMIN en /auth/me');
    const adminMe = await (await authClient.getMe(adminToken)).json();
    expect(adminMe.role).toBe('ADMIN');
    Logger.pass(`Rol ADMIN confirmado: ${adminMe.role}`);

    Logger.step(2, 'Verificar rol AGENT en /auth/me');
    const agentMe = await (await authClient.getMe(agentToken)).json();
    expect(agentMe.role).toBe('AGENT');
    Logger.pass(`Rol AGENT confirmado: ${agentMe.role}`);

    Logger.step(3, 'Verificar rol USER (Customer) en /auth/me');
    const customerMe = await (await authClient.getMe(customerToken)).json();
    expect(customerMe.role).toBe('USER');
    Logger.pass(`Rol Customer confirmado: ${customerMe.role}`);
  });

  test('TC-AUTH-05: Acceso a endpoint protegido sin token → 401', { tag: ['@regression', '@negative'] }, async () => {
    Logger.testCase('TC-AUTH-05', 'Acceso a endpoint protegido sin token → 401');

    Logger.step(1, 'Consultar /auth/me sin token');
    const res = await authClient.getMe('');
    expect(res.status()).toBe(401);
    const body = await res.json();
    expect(body.detail).toMatch(/Not authenticated|inválido/i);
    Logger.pass('Endpoint protegido rechazó acceso anónimo con HTTP 401');
  });

  test('TC-AUTH-06: Acceso con token expirado → 401', { tag: ['@regression', '@negative'] }, async () => {
    Logger.testCase('TC-AUTH-06', 'Acceso con token expirado → 401');

    Logger.step(1, 'Generar token expirado y consultar /auth/me');
    const expiredToken = createExpiredToken();
    const res = await authClient.getMe(expiredToken);
    expect(res.status()).toBe(401);
    const body = await res.json();
    expect(body.detail).toBe('Invalid token');
    Logger.pass('Token expirado rechazado con HTTP 401 e "Invalid token"');
  });

  test('TC-AUTH-07: Acceso con token manipulado (rol alterado, firma inválida) → 401/403', { tag: ['@regression', '@negative'] }, async () => {
    Logger.testCase('TC-AUTH-07', 'Acceso con token manipulado (rol alterado, firma inválida) → 401/403');

    Logger.step(1, 'Manipular payload de token de usuario a ADMIN sin firma válida');
    const tamperedToken = createManipulatedToken(customerToken, { sub: '2', role: 'ADMIN' });
    const res = await authClient.getMe(tamperedToken);
    expect([401, 403]).toContain(res.status());
    Logger.pass(`Token con firma inválida rechazado con HTTP ${res.status()}`);
  });

  test('TC-AUTH-09: Customer no accede a endpoints de Admin → 403', { tag: ['@regression', '@negative'] }, async () => {
    Logger.testCase('TC-AUTH-09', 'Customer no accede a endpoints de Admin → 403');

    Logger.step(1, 'Customer intenta crear categoría en POST /categories');
    const res = await catalogClient.createCategory(customerToken, {
      name: 'Cat Denegada Customer',
      description: 'Intento prohibido',
      requires_approval: false,
    });
    expect(res.status()).toBe(403);
    const body = await res.json();
    expect(body.detail).toMatch(/permisos/i);
    Logger.pass(`Customer bloqueado de endpoints Admin con HTTP 403: "${body.detail}"`);
  });

  test('TC-AUTH-10: Service Agent no accede a endpoints de Admin → 403', { tag: ['@regression', '@negative'] }, async () => {
    Logger.testCase('TC-AUTH-10', 'Service Agent no accede a endpoints de Admin → 403');

    Logger.step(1, 'Agente intenta crear usuario en POST /users');
    const res = await usersClient.createUser(agentToken, {
      name: 'Agent Prohibido',
      email: 'agent_spawn@test.com',
      role_id: 2,
    });
    expect(res.status()).toBe(403);
    const body = await res.json();
    expect(body.detail).toMatch(/permisos/i);
    Logger.pass(`Service Agent bloqueado de endpoints Admin con HTTP 403: "${body.detail}"`);
  });

  test('TC-SYS-01: Validación de campos obligatorios al crear entidades', { tag: ['@regression', '@negative'] }, async () => {
    Logger.testCase('TC-SYS-01', 'Validación de campos obligatorios al crear entidades');

    Logger.step(1, 'Crear categoría con payload vacío {}');
    const res = await catalogClient.createCategory(adminToken, {});
    expect(res.status()).toBe(422);
    const body = await res.json();
    expect(Array.isArray(body.detail)).toBe(true);
    Logger.pass('Validación de campos obligatorios retornó HTTP 422');
  });

  test('TC-SYS-02: Errores 500 no exponen información sensible (stack trace)', { tag: ['@regression', '@negative'] }, async ({ request }) => {
    Logger.testCase('TC-SYS-02', 'Errores 500 no exponen información sensible (stack trace)');

    Logger.step(1, 'Solicitar recurso no existente con ID fuera de rango');
    const res = await request.get('/requests/99999999', {
      headers: { Authorization: `Bearer ${adminToken}` },
    });
    const text = await res.text();
    expect(text).not.toMatch(/Traceback \(most recent call last\)/i);
    expect(text).not.toMatch(/password_hash/i);
    expect(text).not.toMatch(/postgresql\+asyncpg/i);
    Logger.pass(`Respuesta controlada (HTTP ${res.status()}) sin fuga de stacktraces ni secretos`);
  });

  test('TC-SYS-03: API responde con contrato esperado (status codes, formato JSON)', { tag: ['@regression', '@positive'] }, async () => {
    Logger.testCase('TC-SYS-03', 'API responde con contrato esperado (status codes, formato JSON)');

    Logger.step(1, 'Validar contrato de POST /auth/login contra JSON Schema con AJV');
    const loginRes = await authClient.login(TEST_USERS.ADMIN.email, TEST_USERS.ADMIN.password);
    expect(loginRes.status()).toBe(200);
    const loginData = await loginRes.json();
    const loginCheck = validateSchema(loginResponseSchema, loginData, 'LoginResponse');
    expect(loginCheck.valid).toBe(true);

    Logger.step(2, 'Validar contrato de GET /auth/me contra JSON Schema con AJV');
    const meRes = await authClient.getMe(adminToken);
    expect(meRes.status()).toBe(200);
    const meData = await meRes.json();
    const meCheck = validateSchema(userMeResponseSchema, meData, 'UserMeResponse');
    expect(meCheck.valid).toBe(true);
    Logger.pass('Contratos de respuestas JSON validados exitosamente con AJV');
  });

  test('TC-SYS-04: Entorno Docker levanta correctamente todos los servicios', { tag: ['@smoke', '@regression', '@positive'] }, async ({ request }) => {
    Logger.testCase('TC-SYS-04', 'Entorno Docker levanta correctamente todos los servicios');

    Logger.step(1, 'Verificar estado del servicio a través de GET /health');
    const res = await request.get(ENDPOINTS.HEALTH);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body.status).toBe('ok');
    Logger.pass(`Todos los servicios backend y base de datos respondiendo en línea: ${JSON.stringify(body)}`);
  });

  test('TC-SYS-05: Tiempo de respuesta de la API con usuario válido autenticado (tiempo de espera hasta recibir respuesta)', { tag: ['@regression', '@positive'] }, async () => {
    Logger.testCase('TC-SYS-05', 'Tiempo de respuesta de la API con usuario válido autenticado');

    Logger.step(1, 'Medir tiempo de respuesta en login con credenciales válidas');
    const startLogin = Date.now();
    const loginRes = await authClient.login(TEST_USERS.ADMIN.email, TEST_USERS.ADMIN.password);
    const durationLogin = Date.now() - startLogin;

    expect(loginRes.status()).toBe(200);
    expect(durationLogin).toBeLessThan(2000);
    const loginData = await loginRes.json();
    const token = loginData.access_token;
    Logger.pass(`Login completado en ${durationLogin} ms (umbral < 2000 ms)`);

    Logger.step(2, 'Medir tiempo de respuesta en petición autenticada GET /auth/me');
    const startMe = Date.now();
    const meRes = await authClient.getMe(token);
    const durationMe = Date.now() - startMe;

    expect(meRes.status()).toBe(200);
    expect(durationMe).toBeLessThan(1000);
    Logger.pass(`Consulta /auth/me completada en ${durationMe} ms (umbral < 1000 ms)`);
  });
});

