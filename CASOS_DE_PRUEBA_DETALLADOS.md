# Especificación Detallada de Casos de Prueba (Test Cases)
**Estándar de Calidad y Automatización — Ruta QA**
**Proyecto:** ServiceFlow (No Country — S08-26-Equipo-20)
**Autor:** Andres Adrian Estrada
**Total de Casos de Prueba:** 31

---

# Módulo 1: Autenticación y Sistema

---

### Metadatos del Caso de Prueba
- **ID:** `TC-AUTH-04`
- **Módulo / Funcionalidad:** 1. Autenticación y Sistema / Verificación de Roles y Claims en Token
- **Título:** Token Bearer token generado contiene el rol correcto
- **Tipo de Prueba:** Funcional / Positiva
- **Etiquetas:** `@positiva` `@regresiva` `@alta`
- **Prioridad:** Alta
- **Severidad:** Crítica
- **Automatizado:** Sí (Playwright + Node.js)
- **Referencia de Automatización:** `tests/E2E_API/01_autenticacion_sistema.spec.js`
- **Autor:** Andres Adrian Estrada

---

### Precondiciones
1. La API de ServiceFlow debe estar en ejecución y accesible en `http://localhost:8000`.
2. Deben existir usuarios preconfigurados en la base de datos con roles ADMIN, AGENT y USER (Customer).
3. Las credenciales de prueba deben estar cargadas en `data/testUsers.js`.

---

### Datos de Prueba (Test Data)
- **Origen:** `data/testUsers.js` -> `TEST_USERS`
- **Admin:** `admin@serviceflow.com` / `admin123`
- **Agent:** `linder@serviceflow.com` / `agent123`
- **Customer:** `user@serviceflow.com` / `user123`

---

### Pasos de Ejecución (Test Steps)
| Paso # | Acción del Usuario | Datos / Parámetros | Localizador Sugerido |
| :---: | :--- | :--- | :--- |
| **1** | Enviar petición GET con token de ADMIN al endpoint de perfil | Header: `Authorization: Bearer <adminToken>` | `GET /auth/me` |
| **2** | Validar que el campo `role` de la respuesta sea "ADMIN" | Payload JSON de respuesta | `expect(adminMe.role).toBe('ADMIN')` |
| **3** | Enviar petición GET con token de AGENT al endpoint de perfil | Header: `Authorization: Bearer <agentToken>` | `GET /auth/me` |
| **4** | Validar que el campo `role` de la respuesta sea "AGENT" | Payload JSON de respuesta | `expect(agentMe.role).toBe('AGENT')` |
| **5** | Enviar petición GET con token de CUSTOMER al endpoint de perfil | Header: `Authorization: Bearer <customerToken>` | `GET /auth/me` |
| **6** | Validar que el campo `role` de la respuesta sea "USER" | Payload JSON de respuesta | `expect(customerMe.role).toBe('USER')` |

---

### Resultado Esperado
1. Las 3 peticiones responden con código HTTP 200 OK.
2. Cada token JWT decodificado en servidor mapea al rol exacto correspondiente en la base de datos sin discrepancias.

---

### Resultado Actual y Evidencias (Para Ejecución Manual)
- **Estado:** [X] Aprobado (Passed)  [ ] Fallido (Failed)  [ ] Bloqueado (Blocked)
- **Fecha de Ejecución:** 2026-09-29
- **Ejecutado por:** Andres Adrian Estrada
- **Enlace a Evidencias / Capturas:** Reporte Playwright HTML / Allure (`test-results.json`)
- **Defecto Asociado:** N/A

---

### Metadatos del Caso de Prueba
- **ID:** `TC-AUTH-05`
- **Módulo / Funcionalidad:** 1. Autenticación y Sistema / Protección de Endpoints
- **Título:** Acceso a endpoint protegido sin token → 401
- **Tipo de Prueba:** Funcional / Negativa
- **Etiquetas:** `@negativa` `@regresiva` `@alta`
- **Prioridad:** Alta
- **Severidad:** Crítica
- **Automatizado:** Sí (Playwright + Node.js)
- **Referencia de Automatización:** `tests/E2E_API/01_autenticacion_sistema.spec.js`
- **Autor:** Andres Adrian Estrada

---

### Precondiciones
1. La API debe estar desplegada y activa.
2. Endpoint `/auth/me` configurado como recurso protegido mediante dependencia `CurrentUser`.

---

### Datos de Prueba (Test Data)
- **Origen:** Sin cabecera de autenticación
- **Header:** `{}` (vacío / anónimo)

---

### Pasos de Ejecución (Test Steps)
| Paso # | Acción del Usuario | Datos / Parámetros | Localizador Sugerido |
| :---: | :--- | :--- | :--- |
| **1** | Enviar petición GET a endpoint protegido omitiendo cabecera Authorization | Headers sin token Bearer | `GET /auth/me` |
| **2** | Inspeccionar código de estado y cuerpo de error devuelto | N/A | `res.status()`, `res.json()` |

---

### Resultado Esperado
1. El servidor rechaza la solicitud anónima con código HTTP 401 Unauthorized.
2. El cuerpo de respuesta contiene mensaje de detalle descriptivo (`Not authenticated` o similar).

---

### Resultado Actual y Evidencias (Para Ejecución Manual)
- **Estado:** [X] Aprobado (Passed)  [ ] Fallido (Failed)  [ ] Bloqueado (Blocked)
- **Fecha de Ejecución:** 2026-09-29
- **Ejecutado por:** Andres Adrian Estrada
- **Enlace a Evidencias / Capturas:** Reporte Playwright HTML / Allure
- **Defecto Asociado:** N/A

---

### Metadatos del Caso de Prueba
- **ID:** `TC-AUTH-06`
- **Módulo / Funcionalidad:** 1. Autenticación y Sistema / Ciclo de Vida de Tokens
- **Título:** Acceso con token expirado → 401
- **Tipo de Prueba:** Funcional / Negativa
- **Etiquetas:** `@negativa` `@regresiva` `@alta`
- **Prioridad:** Alta
- **Severidad:** Mayor
- **Automatizado:** Sí (Playwright + Node.js)
- **Referencia de Automatización:** `tests/E2E_API/01_autenticacion_sistema.spec.js`
- **Autor:** Andres Adrian Estrada

---

### Precondiciones
1. Servidor de autenticación con validación activa de expiración del claim `exp` en JWT.
2. Utilidad `createExpiredToken()` disponible para firmar token con timestamp en el pasado.

---

### Datos de Prueba (Test Data)
- **Origen:** `data/testUsers.js` -> `createExpiredToken()`
- **Claim exp:** Timestamp actual - 3600 segundos (1 hora en el pasado)

---

### Pasos de Ejecución (Test Steps)
| Paso # | Acción del Usuario | Datos / Parámetros | Localizador Sugerido |
| :---: | :--- | :--- | :--- |
| **1** | Generar token JWT válido pero con fecha de caducidad expirada | `createExpiredToken()` | `data/testUsers.js` |
| **2** | Enviar petición GET con dicho token caducado | Header: `Authorization: Bearer <expiredToken>` | `GET /auth/me` |
| **3** | Validar código de respuesta y mensaje de error | Status HTTP y campo `detail` | `expect(res.status()).toBe(401)` |

---

### Resultado Esperado
1. El servidor rechaza la petición con código HTTP 401 Unauthorized.
2. El mensaje de detalle indica `Invalid token`.

---

### Resultado Actual y Evidencias (Para Ejecución Manual)
- **Estado:** [X] Aprobado (Passed)  [ ] Fallido (Failed)  [ ] Bloqueado (Blocked)
- **Fecha de Ejecución:** 2026-09-29
- **Ejecutado por:** Andres Adrian Estrada
- **Enlace a Evidencias / Capturas:** Reporte Playwright HTML / Allure
- **Defecto Asociado:** N/A

---

### Metadatos del Caso de Prueba
- **ID:** `TC-AUTH-07`
- **Módulo / Funcionalidad:** 1. Autenticación y Sistema / Integridad Criptográfica de JWT
- **Título:** Acceso con token manipulado (rol alterado, firma inválida) → 401/403
- **Tipo de Prueba:** Funcional / Negativa
- **Etiquetas:** `@negativa` `@regresiva` `@alta`
- **Prioridad:** Alta
- **Severidad:** Crítica
- **Automatizado:** Sí (Playwright + Node.js)
- **Referencia de Automatización:** `tests/E2E_API/01_autenticacion_sistema.spec.js`
- **Autor:** Andres Adrian Estrada

---

### Precondiciones
1. Algoritmo HMAC SHA-256 configurado en backend con clave secreta privada.
2. Token legítimo de usuario Customer disponible para alteración.

---

### Datos de Prueba (Test Data)
- **Origen:** `createManipulatedToken(customerToken, { sub: '2', role: 'ADMIN' })`
- **Payload Alterado:** Claims modificados a rol ADMIN sin refirma legítima

---

### Pasos de Ejecución (Test Steps)
| Paso # | Acción del Usuario | Datos / Parámetros | Localizador Sugerido |
| :---: | :--- | :--- | :--- |
| **1** | Decodificar payload de token legítimo y alterar claim `role` a "ADMIN" | Payload alterado | `createManipulatedToken()` |
| **2** | Enviar petición GET con token adulterado conservando firma anterior | Header: `Authorization: Bearer <tamperedToken>` | `GET /auth/me` |
| **3** | Verificar que el backend verifique la firma criptográfica y rechace | Códigos HTTP 401 o 403 | `expect([401, 403]).toContain(res.status())` |

---

### Resultado Esperado
1. La firma criptográfica no coincide con el payload adulterado.
2. El backend rechaza el acceso inmediatamente devolviendo HTTP 401 Unauthorized o 403 Forbidden.

---

### Resultado Actual y Evidencias (Para Ejecución Manual)
- **Estado:** [X] Aprobado (Passed)  [ ] Fallido (Failed)  [ ] Bloqueado (Blocked)
- **Fecha de Ejecución:** 2026-09-29
- **Ejecutado por:** Andres Adrian Estrada
- **Enlace a Evidencias / Capturas:** Reporte Playwright HTML / Allure
- **Defecto Asociado:** N/A

---

### Metadatos del Caso de Prueba
- **ID:** `TC-AUTH-09`
- **Módulo / Funcionalidad:** 1. Autenticación y Sistema / Control de Acceso RBAC (Customer vs Admin)
- **Título:** Customer no accede a endpoints de Admin → 403
- **Tipo de Prueba:** Funcional / Negativa
- **Etiquetas:** `@negativa` `@regresiva` `@alta`
- **Prioridad:** Alta
- **Severidad:** Crítica
- **Automatizado:** Sí (Playwright + Node.js)
- **Referencia de Automatización:** `tests/E2E_API/01_autenticacion_sistema.spec.js`
- **Autor:** Andres Adrian Estrada

---

### Precondiciones
1. Usuario con rol USER (Customer) autenticado en el sistema.
2. Endpoint `POST /categories` protegido exclusivamente para rol ADMIN.

---

### Datos de Prueba (Test Data)
- **Token:** Bearer Token de Customer
- **Payload:** `{"name": "Cat Denegada Customer", "description": "Intento prohibido", "requires_approval": false}`

---

### Pasos de Ejecución (Test Steps)
| Paso # | Acción del Usuario | Datos / Parámetros | Localizador Sugerido |
| :---: | :--- | :--- | :--- |
| **1** | Enviar petición POST a `/categories` utilizando token de rol Customer | Token de Customer + Payload de categoría | `POST /categories` |
| **2** | Comprobar código de estado HTTP y cuerpo de error | Validación de rechazo RBAC | `expect(res.status()).toBe(403)` |

---

### Resultado Esperado
1. El backend bloquea el acceso con código HTTP 403 Forbidden.
2. El cuerpo de respuesta indica falta de permisos para la operación.

---

### Resultado Actual y Evidencias (Para Ejecución Manual)
- **Estado:** [X] Aprobado (Passed)  [ ] Fallido (Failed)  [ ] Bloqueado (Blocked)
- **Fecha de Ejecución:** 2026-09-29
- **Ejecutado por:** Andres Adrian Estrada
- **Enlace a Evidencias / Capturas:** Reporte Playwright HTML / Allure
- **Defecto Asociado:** N/A

---

### Metadatos del Caso de Prueba
- **ID:** `TC-AUTH-10`
- **Módulo / Funcionalidad:** 1. Autenticación y Sistema / Control de Acceso RBAC (Agent vs Admin)
- **Título:** Service Agent no accede a endpoints de Admin → 403
- **Tipo de Prueba:** Funcional / Negativa
- **Etiquetas:** `@negativa` `@regresiva` `@alta`
- **Prioridad:** Alta
- **Severidad:** Crítica
- **Automatizado:** Sí (Playwright + Node.js)
- **Referencia de Automatización:** `tests/E2E_API/01_autenticacion_sistema.spec.js`
- **Autor:** Andres Adrian Estrada

---

### Precondiciones
1. Usuario con rol AGENT autenticado en el sistema.
2. Endpoint `POST /users` protegido exclusivamente para rol ADMIN.

---

### Datos de Prueba (Test Data)
- **Token:** Bearer Token de Agent
- **Payload:** `{"name": "Agent Prohibido", "email": "agent_spawn@test.com", "role_id": 2}`

---

### Pasos de Ejecución (Test Steps)
| Paso # | Acción del Usuario | Datos / Parámetros | Localizador Sugerido |
| :---: | :--- | :--- | :--- |
| **1** | Enviar petición POST a `/users` utilizando token de Service Agent | Token de Agent + Payload de usuario | `POST /users` |
| **2** | Comprobar código de estado HTTP devuelto | Verificación de código 403 | `expect(res.status()).toBe(403)` |

---

### Resultado Esperado
1. El backend bloquea la creación con código HTTP 403 Forbidden.
2. El mensaje especifica ausencia de privilegios de administrador.

---

### Resultado Actual y Evidencias (Para Ejecución Manual)
- **Estado:** [X] Aprobado (Passed)  [ ] Fallido (Failed)  [ ] Bloqueado (Blocked)
- **Fecha de Ejecución:** 2026-09-29
- **Ejecutado por:** Andres Adrian Estrada
- **Enlace a Evidencias / Capturas:** Reporte Playwright HTML / Allure
- **Defecto Asociado:** N/A

---

### Metadatos del Caso de Prueba
- **ID:** `TC-SYS-01`
- **Módulo / Funcionalidad:** 1. Autenticación y Sistema / Validación de Esquemas y Payload
- **Título:** Validación de campos obligatorios al crear entidades
- **Tipo de Prueba:** Funcional / Negativa
- **Etiquetas:** `@negativa` `@regresiva` `@media`
- **Prioridad:** Media
- **Severidad:** Media
- **Automatizado:** Sí (Playwright + Node.js)
- **Referencia de Automatización:** `tests/E2E_API/01_autenticacion_sistema.spec.js`
- **Autor:** Andres Adrian Estrada

---

### Precondiciones
1. Usuario ADMIN autenticado con token válido.
2. Esquema Pydantic con validadores de campos obligatorios (`Field(...)`).

---

### Datos de Prueba (Test Data)
- **Token:** Bearer Token de Admin
- **Payload:** `{}` (objeto vacío, sin campos requeridos)

---

### Pasos de Ejecución (Test Steps)
| Paso # | Acción del Usuario | Datos / Parámetros | Localizador Sugerido |
| :---: | :--- | :--- | :--- |
| **1** | Enviar petición POST a `/categories` con payload vacío `{}` | Token de Admin + Body `{}` | `POST /categories` |
| **2** | Verificar código de respuesta HTTP | Código esperado HTTP 422 | `expect(res.status()).toBe(422)` |
| **3** | Comprobar estructura de errores de validación en `detail` | Lista de errores de validación | `expect(Array.isArray(body.detail)).toBe(true)` |

---

### Resultado Esperado
1. El servidor devuelve HTTP 422 Unprocessable Entity.
2. La respuesta incluye lista detallada de campos requeridos ausentes.

---

### Resultado Actual y Evidencias (Para Ejecución Manual)
- **Estado:** [X] Aprobado (Passed)  [ ] Fallido (Failed)  [ ] Bloqueado (Blocked)
- **Fecha de Ejecución:** 2026-09-29
- **Ejecutado por:** Andres Adrian Estrada
- **Enlace a Evidencias / Capturas:** Reporte Playwright HTML / Allure
- **Defecto Asociado:** N/A

---

### Metadatos del Caso de Prueba
- **ID:** `TC-SYS-02`
- **Módulo / Funcionalidad:** 1. Autenticación y Sistema / Fuga de Información y Manejo de Errores
- **Título:** Error 404 no exponen información sensible (stack trace)
- **Tipo de Prueba:** Funcional / Negativa
- **Etiquetas:** `@negativa` `@regresiva` `@media`
- **Prioridad:** Media
- **Severidad:** Mayor
- **Automatizado:** Sí (Playwright + Node.js)
- **Referencia de Automatización:** `tests/E2E_API/01_autenticacion_sistema.spec.js`
- **Autor:** Andres Adrian Estrada

---

### Precondiciones
1. Servidor configurado con manejadores de excepciones centralizados.
2. Token de usuario autenticado disponible.

---

### Datos de Prueba (Test Data)
- **ID de Recurso Inexistente:** `99999999`
- **Endpoint:** `/requests/99999999`

---

### Pasos de Ejecución (Test Steps)
| Paso # | Acción del Usuario | Datos / Parámetros | Localizador Sugerido |
| :---: | :--- | :--- | :--- |
| **1** | Solicitar recurso no existente con ID fuera de rango | `GET /requests/99999999` con Bearer Admin | `GET /requests/99999999` |
| **2** | Inspeccionar cuerpo de texto de la respuesta | Contenido textual de error | `res.text()` |
| **3** | Verificar ausencia de trazas internas de Python/SQLAlchemy | Validar contra regex `Traceback`, `password_hash`, `asyncpg` | `expect(text).not.toMatch(...)` |

---

### Resultado Esperado
1. La respuesta es manejada de forma controlada sin volcar stack traces de Python (`Traceback (most recent call last)`).
2. No se filtran cadenas de conexión, secretos ni nombres de tablas internas.

---

### Resultado Actual y Evidencias (Para Ejecución Manual)
- **Estado:** [X] Aprobado (Passed)  [ ] Fallido (Failed)  [ ] Bloqueado (Blocked)
- **Fecha de Ejecución:** 2026-09-29
- **Ejecutado por:** Andres Adrian Estrada
- **Enlace a Evidencias / Capturas:** Reporte Playwright HTML / Allure
- **Defecto Asociado:** N/A

---

### Metadatos del Caso de Prueba
- **ID:** `TC-SYS-03`
- **Módulo / Funcionalidad:** 1. Autenticación y Sistema / Validación de Contratos JSON (Schema Testing)
- **Título:** API responde con contrato esperado (status codes, formato JSON)
- **Tipo de Prueba:** Funcional / Positiva
- **Etiquetas:** `@positiva` `@regresiva` `@media`
- **Prioridad:** Media
- **Severidad:** Mayor
- **Automatizado:** Sí (Playwright + Node.js + AJV)
- **Referencia de Automatización:** `tests/E2E_API/01_autenticacion_sistema.spec.js`
- **Autor:** Andres Adrian Estrada

---

### Precondiciones
1. Esquemas JSON Schema formalizados en `schemas/auth.schema.js`.
2. Validador AJV configurado con tipos estrictos.

---

### Datos de Prueba (Test Data)
- **Login Schema:** `schemas/auth.schema.js` -> `loginResponseSchema`
- **User Me Schema:** `schemas/auth.schema.js` -> `userMeResponseSchema`
- **Credenciales:** `admin@serviceflow.com` / `admin123`

---

### Pasos de Ejecución (Test Steps)
| Paso # | Acción del Usuario | Datos / Parámetros | Localizador Sugerido |
| :---: | :--- | :--- | :--- |
| **1** | Enviar login con credenciales válidas y validar JSON Schema con AJV | `POST /auth/login` | `validateSchema(loginResponseSchema, loginData)` |
| **2** | Enviar consulta de perfil y validar JSON Schema con AJV | `GET /auth/me` | `validateSchema(userMeResponseSchema, meData)` |

---

### Resultado Esperado
1. Ambas respuestas tienen status 200 OK y cumplen al 100% las restricciones de tipos, propiedades obligatorias y formatos.

---

### Resultado Actual y Evidencias (Para Ejecución Manual)
- **Estado:** [X] Aprobado (Passed)  [ ] Fallido (Failed)  [ ] Bloqueado (Blocked)
- **Fecha de Ejecución:** 2026-09-29
- **Ejecutado por:** Andres Adrian Estrada
- **Enlace a Evidencias / Capturas:** Reporte Playwright HTML / Allure
- **Defecto Asociado:** N/A

---

### Metadatos del Caso de Prueba
- **ID:** `TC-SYS-04`
- **Módulo / Funcionalidad:** 1. Autenticación y Sistema / Infraestructura y Salud de Servicios
- **Título:** Entorno Docker levanta correctamente todos los servicios
- **Tipo de Prueba:** Funcional / Positiva
- **Etiquetas:** `@positiva` `@regresiva` `@alta`
- **Prioridad:** Alta
- **Severidad:** Crítica
- **Automatizado:** Sí (Playwright + Node.js)
- **Referencia de Automatización:** `tests/E2E_API/01_autenticacion_sistema.spec.js`
- **Autor:** Andres Adrian Estrada

---

### Precondiciones
1. Servicios backend FastAPI y PostgreSQL iniciados y conectados.

---

### Datos de Prueba (Test Data)
- **Endpoint:** `GET /health`
- **Headers:** `{}` (acceso público sin autenticación)

---

### Pasos de Ejecución (Test Steps)
| Paso # | Acción del Usuario | Datos / Parámetros | Localizador Sugerido |
| :---: | :--- | :--- | :--- |
| **1** | Realizar petición GET al endpoint de verificación de salud | `GET /health` | `request.get(ENDPOINTS.HEALTH)` |
| **2** | Validar código de respuesta HTTP | Status esperado HTTP 200 | `expect(res.status()).toBe(200)` |
| **3** | Validar propiedad de estado en cuerpo JSON | `{"status": "ok"}` | `expect(body.status).toBe('ok')` |

---

### Resultado Esperado
1. La API responde con HTTP 200 OK y cuerpo `{"status": "ok"}` confirmando salud operativa.

---

### Resultado Actual y Evidencias (Para Ejecución Manual)
- **Estado:** [X] Aprobado (Passed)  [ ] Fallido (Failed)  [ ] Bloqueado (Blocked)
- **Fecha de Ejecución:** 2026-09-29
- **Ejecutado por:** Andres Adrian Estrada
- **Enlace a Evidencias / Capturas:** Reporte Playwright HTML / Allure
- **Defecto Asociado:** N/A

---

### Metadatos del Caso de Prueba
- **ID:** `TC-SYS-05`
- **Módulo / Funcionalidad:** 1. Autenticación y Sistema / Rendimiento y Tiempo de Respuesta de la API
- **Título:** Tiempo de respuesta de la API con usuario válido autenticado (tiempo de espera hasta recibir respuesta)
- **Tipo de Prueba:** Funcional / Positiva
- **Etiquetas:** `@positiva` `@regresiva` `@media`
- **Prioridad:** Media
- **Severidad:** Mayor
- **Automatizado:** Sí (Playwright + Node.js)
- **Referencia de Automatización:** `tests/E2E_API/01_autenticacion_sistema.spec.js`
- **Autor:** Andres Adrian Estrada

---

### Precondiciones
1. El backend debe estar desplegado y con conexión activa a base de datos.
2. Usuario válido registrado con credenciales correctas en `data/testUsers.js`.

---

### Datos de Prueba (Test Data)
- **Email:** `admin@serviceflow.com`
- **Contraseña:** `admin123`
- **Umbral de Latencia Login:** < 2000 ms
- **Umbral de Latencia Petición Autenticada:** < 1000 ms

---

### Pasos de Ejecución (Test Steps)
| Paso # | Acción del Usuario | Datos / Parámetros | Localizador Sugerido |
| :---: | :--- | :--- | :--- |
| **1** | Iniciar temporizador de alta precisión | `startLogin = Date.now()` | Javascript timestamp |
| **2** | Ejecutar petición de login con credenciales válidas | `POST /auth/login` con email y contraseña | `authClient.login(...)` |
| **3** | Calcular delta de tiempo y validar latencia aceptable | `durationLogin = Date.now() - startLogin` | `expect(durationLogin).toBeLessThan(2000)` |
| **4** | Iniciar temporizador para endpoint autenticado | `startMe = Date.now()` | Javascript timestamp |
| **5** | Ejecutar petición GET `/auth/me` con Bearer Token recibido | Header `Authorization: Bearer <token>` | `authClient.getMe(...)` |
| **6** | Calcular delta de tiempo y validar latencia aceptable | `durationMe = Date.now() - startMe` | `expect(durationMe).toBeLessThan(1000)` |

---

### Resultado Esperado
1. El login responde en menos de 2000 ms con HTTP 200 y token Bearer válido.
2. La consulta autenticada `/auth/me` responde en menos de 1000 ms con HTTP 200.
3. Se registra en consola la duración exacta en milisegundos para monitoreo.

---

### Resultado Actual y Evidencias (Para Ejecución Manual)
- **Estado:** [X] Aprobado (Passed)  [ ] Fallido (Failed)  [ ] Bloqueado (Blocked)
- **Fecha de Ejecución:** 2026-09-29
- **Ejecutado por:** Andres Adrian Estrada
- **Enlace a Evidencias / Capturas:** Reporte Playwright HTML / Allure (Login: ~54 ms, /auth/me: ~8 ms)
- **Defecto Asociado:** N/A

---

# Módulo 2: Customer — Solicitudes

---

### Metadatos del Caso de Prueba
- **ID:** `TC-CUST-05`
- **Módulo / Funcionalidad:** 2. Customer: Solicitudes / Seguridad y Control de Acceso IDOR
- **Título:** Ver detalle de solicitud de otro customer → 403/404 (IDOR)
- **Tipo de Prueba:** Funcional / Negativa
- **Etiquetas:** `@negativa` `@regresiva` `@alta`
- **Prioridad:** Alta
- **Severidad:** Crítica
- **Automatizado:** Sí (Playwright + Node.js)
- **Referencia de Automatización:** `tests/E2E_API/02_customer_solicitudes.spec.js`
- **Autor:** Andres Adrian Estrada

---

### Precondiciones
1. Customer A crea una solicitud con ID conocido en el sistema.
2. Customer B está autenticado con su propia cuenta y sesión independiente.

---

### Datos de Prueba (Test Data)
- **Customer A:** `user@serviceflow.com` (Creador de la solicitud)
- **Customer B:** `cust_b_<unique>@test.com` (Usuario no autorizado)
- **Solicitud Objetivo:** ID creado por Customer A

---

### Pasos de Ejecución (Test Steps)
| Paso # | Acción del Usuario | Datos / Parámetros | Localizador Sugerido |
| :---: | :--- | :--- | :--- |
| **1** | Customer B intenta consultar la solicitud de Customer A por ID | Header `Authorization: Bearer <customerBToken>` | `GET /customer/requests/{requestAId}` |
| **2** | Inspeccionar código de estado y cuerpo de error | Validación de rechazo IDOR | `expect([403, 404]).toContain(res.status())` |

---

### Resultado Esperado
1. El backend deniega el acceso retornando código HTTP 403 Forbidden o 404 Not Found.
2. Mensaje de error indica: *"Acceso denegado: esta solicitud pertenece a otro usuario."*.

---

### Resultado Actual y Evidencias (Para Ejecución Manual)
- **Estado:** [X] Aprobado (Passed)  [ ] Fallido (Failed)  [ ] Bloqueado (Blocked)
- **Fecha de Ejecución:** 2026-09-29
- **Ejecutado por:** Andres Adrian Estrada
- **Enlace a Evidencias / Capturas:** Reporte Playwright HTML / Allure
- **Defecto Asociado:** N/A

---

### Metadatos del Caso de Prueba
- **ID:** `TC-CUST-10`
- **Módulo / Funcionalidad:** 2. Customer: Solicitudes / Integridad de Comentarios y Privacidad
- **Título:** Agregar comentario a solicitud de otro customer → rechazado
- **Tipo de Prueba:** Funcional / Negativa
- **Etiquetas:** `@negativa` `@regresiva` `@alta`
- **Prioridad:** Alta
- **Severidad:** Alta
- **Automatizado:** Sí (Playwright + Node.js)
- **Referencia de Automatización:** `tests/E2E_API/02_customer_solicitudes.spec.js`
- **Autor:** Andres Adrian Estrada

---

### Precondiciones
1. Customer A tiene una solicitud activa en el sistema.
2. Customer B posee credenciales y token válidos de rol Customer.

---

### Datos de Prueba (Test Data)
- **Customer B Token:** Token de usuario no propietario
- **Payload Comentario:** `{"content": "Comentario no autorizado de otro usuario"}`

---

### Pasos de Ejecución (Test Steps)
| Paso # | Acción del Usuario | Datos / Parámetros | Localizador Sugerido |
| :---: | :--- | :--- | :--- |
| **1** | Customer B envía petición POST para comentar en solicitud ajena | `POST /customer/requests/{requestAId}/comments` | `customerClient.addComment(...)` |
| **2** | Comprobar código de error devuelto por la API | Status HTTP 403 o 404 | `expect([403, 404]).toContain(res.status())` |

---

### Resultado Esperado
1. El servidor bloquea la inserción del comentario con HTTP 403 Forbidden o 404 Not Found.
2. No se altera la conversación de la solicitud.

---

### Resultado Actual y Evidencias (Para Ejecución Manual)
- **Estado:** [X] Aprobado (Passed)  [ ] Fallido (Failed)  [ ] Bloqueado (Blocked)
- **Fecha de Ejecución:** 2026-09-29
- **Ejecutado por:** Andres Adrian Estrada
- **Enlace a Evidencias / Capturas:** Reporte Playwright HTML / Allure
- **Defecto Asociado:** N/A

---

# Módulo 3: Service Agent

---

### Metadatos del Caso de Prueba
- **ID:** `TC-AGENT-09`
- **Módulo / Funcionalidad:** 3. Service Agent / Máquina de Estados de Solicitudes
- **Título:** Cambio de estado inválido (ej. Cerrada→Nueva) → rechazado
- **Tipo de Prueba:** Funcional / Negativa
- **Etiquetas:** `@negativa` `@regresiva` `@media`
- **Prioridad:** Media
- **Severidad:** Mayor
- **Automatizado:** Sí (Playwright + Node.js)
- **Referencia de Automatización:** `tests/E2E_API/03_service_agent.spec.js`
- **Autor:** Andres Adrian Estrada

---

### Precondiciones
1. Solicitud existente registrada en el sistema.
2. Agente con permisos asignados para actualizar estados.

---

### Datos de Prueba (Test Data)
- **Payload:** `{"status": "INVALID_STATE"}`
- **Endpoint:** `PATCH /requests/{id}/status`

---

### Pasos de Ejecución (Test Steps)
| Paso # | Acción del Usuario | Datos / Parámetros | Localizador Sugerido |
| :---: | :--- | :--- | :--- |
| **1** | Agente intenta transicionar solicitud a un estado no contemplado en el Enum | `PATCH /requests/{requestId}/status` con `status: INVALID_STATE` | `requestsClient.changeStatus(...)` |
| **2** | Validar código de error | Status HTTP 400 Bad Request o 422 Unprocessable Entity | `expect([400, 422]).toContain(res.status())` |

---

### Resultado Esperado
1. La API rechaza el cambio inválido devolviendo HTTP 400 o 422.
2. La solicitud mantiene su estado anterior sin corromperse.

---

### Resultado Actual y Evidencias (Para Ejecución Manual)
- **Estado:** [X] Aprobado (Passed)  [ ] Fallido (Failed)  [ ] Bloqueado (Blocked)
- **Fecha de Ejecución:** 2026-09-29
- **Ejecutado por:** Andres Adrian Estrada
- **Enlace a Evidencias / Capturas:** Reporte Playwright HTML / Allure
- **Defecto Asociado:** N/A

---

### Metadatos del Caso de Prueba
- **ID:** `TC-AGENT-10`
- **Módulo / Funcionalidad:** 3. Service Agent / Resolución de Tickets y Trazabilidad Temporal
- **Título:** Resolver solicitud y validar timestamp de resolución
- **Tipo de Prueba:** Funcional / Positiva
- **Etiquetas:** `@positiva` `@regresiva` `@alta`
- **Prioridad:** Alta
- **Severidad:** Mayor
- **Automatizado:** Sí (Playwright + Node.js)
- **Referencia de Automatización:** `tests/E2E_API/03_service_agent.spec.js`
- **Autor:** Andres Adrian Estrada

---

### Precondiciones
1. Solicitud activa en estado NEW o IN_PROGRESS.
2. Agente autenticado con permisos de resolución.

---

### Datos de Prueba (Test Data)
- **Payload:** `{"status": "RESOLVED"}`
- **Expresión Regular ISO 8601:** `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}`

---

### Pasos de Ejecución (Test Steps)
| Paso # | Acción del Usuario | Datos / Parámetros | Localizador Sugerido |
| :---: | :--- | :--- | :--- |
| **1** | Agente envía solicitud de cambio de estado a RESOLVED | `PATCH /requests/{requestId}/status` con `RESOLVED` | `requestsClient.changeStatus(...)` |
| **2** | Comprobar código de respuesta HTTP 200 | Status de respuesta | `expect(res.status()).toBe(200)` |
| **3** | Validar que el campo `resolved_at` contenga un timestamp válido en UTC | Formato ISO 8601 | `expect(data.resolved_at).toMatch(isoRegex)` |

---

### Resultado Esperado
1. La solicitud pasa exitosamente a estado `RESOLVED`.
2. Se genera y persiste automáticamente el timestamp `resolved_at` en formato estándar.

---

### Resultado Actual y Evidencias (Para Ejecución Manual)
- **Estado:** [X] Aprobado (Passed)  [ ] Fallido (Failed)  [ ] Bloqueado (Blocked)
- **Fecha de Ejecución:** 2026-09-29
- **Ejecutado por:** Andres Adrian Estrada
- **Enlace a Evidencias / Capturas:** Reporte Playwright HTML / Allure
- **Defecto Asociado:** N/A

---

### Metadatos del Caso de Prueba
- **ID:** `TC-AGENT-12`
- **Módulo / Funcionalidad:** 3. Service Agent / Notas Internas Confidenciales
- **Título:** Agregar nota interna NO visible para el customer
- **Tipo de Prueba:** Funcional / Positiva
- **Etiquetas:** `@positiva` `@regresiva` `@alta`
- **Prioridad:** Alta
- **Severidad:** Mayor
- **Automatizado:** Sí (Playwright + Node.js)
- **Referencia de Automatización:** `tests/E2E_API/03_service_agent.spec.js`
- **Autor:** Andres Adrian Estrada

---

### Precondiciones
1. Solicitud creada por un Customer.
2. Agente autenticado y asignado.

---

### Datos de Prueba (Test Data)
- **Payload Agente:** `{"content": "Nota interna confidencial para el equipo.", "is_internal": true}`

---

### Pasos de Ejecución (Test Steps)
| Paso # | Acción del Usuario | Datos / Parámetros | Localizador Sugerido |
| :---: | :--- | :--- | :--- |
| **1** | Agente agrega un comentario con marca `is_internal: true` | `POST /requests/{requestId}/comments` | `requestsClient.addComment(...)` |
| **2** | Customer consulta la lista de comentarios de su solicitud | `GET /requests/{requestId}/comments` con token de Customer | `requestsClient.listComments(...)` |
| **3** | Validar que ningún comentario devuelto contenga `is_internal: true` | Array filtrado | `expect(leaked).toBe(false)` |

---

### Resultado Esperado
1. La nota interna se guarda con código HTTP 201 Created.
2. La vista del cliente excluye rigurosamente todas las notas marcadas como internas.

---

### Resultado Actual y Evidencias (Para Ejecución Manual)
- **Estado:** [X] Aprobado (Passed)  [ ] Fallido (Failed)  [ ] Bloqueado (Blocked)
- **Fecha de Ejecución:** 2026-09-29
- **Ejecutado por:** Andres Adrian Estrada
- **Enlace a Evidencias / Capturas:** Reporte Playwright HTML / Allure
- **Defecto Asociado:** N/A

---

# Módulo 4: SLA

---

### Metadatos del Caso de Prueba
- **ID:** `TC-SLA-01`
- **Módulo / Funcionalidad:** 4. SLA / Cálculo de Deadlines de Respuesta y Resolución
- **Título:** SLA se calcula correctamente según categoría/prioridad al crear
- **Tipo de Prueba:** Funcional / Positiva
- **Etiquetas:** `@positiva` `@regresiva` `@alta`
- **Prioridad:** Alta
- **Severidad:** Crítica
- **Automatizado:** Sí (Playwright + Node.js)
- **Referencia de Automatización:** `tests/E2E_API/04_sla.spec.js`
- **Autor:** Andres Adrian Estrada

---

### Precondiciones
1. Categoría y Prioridad creadas con reglas de SLA asociadas.
2. Solicitud clasificada y asignada a un agente.

---

### Datos de Prueba (Test Data)
- **Endpoint:** `GET /requests/{requestId}/sla`
- **Token:** Bearer Token de Agente

---

### Pasos de Ejecución (Test Steps)
| Paso # | Acción del Usuario | Datos / Parámetros | Localizador Sugerido |
| :---: | :--- | :--- | :--- |
| **1** | Consultar registro de SLA de la solicitud clasificada | `GET /requests/{requestId}/sla` | `requestsClient.getSla(...)` |
| **2** | Validar código de respuesta HTTP 200 OK | Código 200 | `expect(slaRes.status()).toBe(200)` |
| **3** | Comprobar que `response_deadline` y `resolution_deadline` no sean nulos | Campos no vacíos | `expect(sla.response_deadline).not.toBeNull()` |

---

### Resultado Esperado
1. El backend calcula y devuelve los plazos límite (`response_deadline` y `resolution_deadline`) calculados a partir de los tiempos configurados.

---

### Resultado Actual y Evidencias (Para Ejecución Manual)
- **Estado:** [X] Aprobado (Passed)  [ ] Fallido (Failed)  [ ] Bloqueado (Blocked)
- **Fecha de Ejecución:** 2026-09-29
- **Ejecutado por:** Andres Adrian Estrada
- **Enlace a Evidencias / Capturas:** Reporte Playwright HTML / Allure
- **Defecto Asociado:** N/A

---

### Metadatos del Caso de Prueba
- **ID:** `TC-SLA-05`
- **Módulo / Funcionalidad:** 4. SLA / Registro de Primera Respuesta
- **Título:** Registra tiempo de primera respuesta del agente
- **Tipo de Prueba:** Funcional / Positiva
- **Etiquetas:** `@positiva` `@regresiva` `@media`
- **Prioridad:** Media
- **Severidad:** Mayor
- **Automatizado:** Sí (Playwright + Node.js)
- **Referencia de Automatización:** `tests/E2E_API/04_sla.spec.js`
- **Autor:** Andres Adrian Estrada

---

### Precondiciones
1. Solicitud asignada y clasificada por el agente técnico.

---

### Datos de Prueba (Test Data)
- **Endpoint:** `GET /requests/{requestId}/sla`

---

### Pasos de Ejecución (Test Steps)
| Paso # | Acción del Usuario | Datos / Parámetros | Localizador Sugerido |
| :---: | :--- | :--- | :--- |
| **1** | Consultar SLA de la solicitud tras la primera interacción del agente | `GET /requests/{requestId}/sla` | `requestsClient.getSla(...)` |
| **2** | Verificar que `responded_at` contenga la marca de tiempo de la respuesta | Campo de fecha | `expect(sla.responded_at).not.toBeNull()` |

---

### Resultado Esperado
1. El sistema persiste la fecha y hora exacta en `responded_at`, deteniendo el cómputo de primera respuesta.

---

### Resultado Actual y Evidencias (Para Ejecución Manual)
- **Estado:** [X] Aprobado (Passed)  [ ] Fallido (Failed)  [ ] Bloqueado (Blocked)
- **Fecha de Ejecución:** 2026-09-29
- **Ejecutado por:** Andres Adrian Estrada
- **Enlace a Evidencias / Capturas:** Reporte Playwright HTML / Allure
- **Defecto Asociado:** N/A

---

### Metadatos del Caso de Prueba
- **ID:** `TC-SLA-06`
- **Módulo / Funcionalidad:** 4. SLA / Registro de Tiempo de Resolución
- **Título:** Registra tiempo de resolución al cerrar la solicitud
- **Tipo de Prueba:** Funcional / Positiva
- **Etiquetas:** `@positiva` `@regresiva` `@media`
- **Prioridad:** Media
- **Severidad:** Mayor
- **Automatizado:** Sí (Playwright + Node.js)
- **Referencia de Automatización:** `tests/E2E_API/04_sla.spec.js`
- **Autor:** Andres Adrian Estrada

---

### Precondiciones
1. Solicitud en proceso de atención con SLA activo.

---

### Datos de Prueba (Test Data)
- **Payload Estado:** `{"status": "RESOLVED"}`

---

### Pasos de Ejecución (Test Steps)
| Paso # | Acción del Usuario | Datos / Parámetros | Localizador Sugerido |
| :---: | :--- | :--- | :--- |
| **1** | Agente transiciona solicitud a estado RESOLVED | `PATCH /requests/{requestId}/status` | `requestsClient.changeStatus(...)` |
| **2** | Consultar SLA asociado a la solicitud | `GET /requests/{requestId}/sla` | `requestsClient.getSla(...)` |
| **3** | Validar que el campo `resolved_at` esté registrado con valor no nulo | Timestamp de resolución | `expect(sla.resolved_at).not.toBeNull()` |

---

### Resultado Esperado
1. Al resolver el ticket, el SLA registra el timestamp final en `resolved_at` para cálculo de métricas de cumplimiento.

---

### Resultado Actual y Evidencias (Para Ejecución Manual)
- **Estado:** [X] Aprobado (Passed)  [ ] Fallido (Failed)  [ ] Bloqueado (Blocked)
- **Fecha de Ejecución:** 2026-09-29
- **Ejecutado por:** Andres Adrian Estrada
- **Enlace a Evidencias / Capturas:** Reporte Playwright HTML / Allure
- **Defecto Asociado:** N/A

---

### Metadatos del Caso de Prueba
- **ID:** `TC-SLA-07`
- **Módulo / Funcionalidad:** 4. SLA / Formato UTC y Booleanos de Cumplimiento
- **Título:** Cálculo correcto con husos horarios / fines de semana
- **Tipo de Prueba:** Funcional / Positiva
- **Etiquetas:** `@positiva` `@regresiva` `@media`
- **Prioridad:** Media
- **Severidad:** Media
- **Automatizado:** Sí (Playwright + Node.js)
- **Referencia de Automatización:** `tests/E2E_API/04_sla.spec.js`
- **Autor:** Andres Adrian Estrada

---

### Precondiciones
1. Registro de SLA completo generado en base de datos.

---

### Datos de Prueba (Test Data)
- **Formato Esperado:** ISO 8601 UTC (`YYYY-MM-DDTHH:MM:SS`)

---

### Pasos de Ejecución (Test Steps)
| Paso # | Acción del Usuario | Datos / Parámetros | Localizador Sugerido |
| :---: | :--- | :--- | :--- |
| **1** | Consultar detalle completo de SLA | `GET /requests/{requestId}/sla` | `requestsClient.getSla(...)` |
| **2** | Validar que todos los campos temporales cumplan formato ISO 8601 | Regex ISO 8601 en `response_deadline`, `resolution_deadline`, etc. | `expect(sla.response_deadline).toMatch(isoRegex)` |
| **3** | Validar que `response_on_time` y `resolution_on_time` sean de tipo booleano | Tipos de datos booleanos | `expect(typeof sla.response_on_time).toBe('boolean')` |

---

### Resultado Esperado
1. Todos los timestamps están estandarizados en UTC bajo norma ISO 8601.
2. Los flags de cumplimiento contienen valores booleanos (`true`/`false`).

---

### Resultado Actual y Evidencias (Para Ejecución Manual)
- **Estado:** [X] Aprobado (Passed)  [ ] Fallido (Failed)  [ ] Bloqueado (Blocked)
- **Fecha de Ejecución:** 2026-09-29
- **Ejecutado por:** Andres Adrian Estrada
- **Enlace a Evidencias / Capturas:** Reporte Playwright HTML / Allure
- **Defecto Asociado:** N/A

---

# Módulo 5: Aprobaciones

---

### Metadatos del Caso de Prueba
- **ID:** `TC-APR-01`
- **Módulo / Funcionalidad:** 5. Aprobaciones / Disparo Automático por Categoría
- **Título:** Categoría "Requiere Aprobación=true" dispara el flujo automáticamente
- **Tipo de Prueba:** Funcional / Positiva
- **Etiquetas:** `@positiva` `@regresiva` `@alta`
- **Prioridad:** Alta
- **Severidad:** Crítica
- **Automatizado:** Sí (Playwright + Node.js)
- **Referencia de Automatización:** `tests/E2E_API/05_aprobaciones.spec.js`
- **Autor:** Andres Adrian Estrada

---

### Precondiciones
1. Categoría configurada con flag `requires_approval: true`.
2. Solicitud creada pendiente de clasificación.

---

### Datos de Prueba (Test Data)
- **Payload Clasificación:** `{"category_id": <catWithApprovalId>}`

---

### Pasos de Ejecución (Test Steps)
| Paso # | Acción del Usuario | Datos / Parámetros | Localizador Sugerido |
| :---: | :--- | :--- | :--- |
| **1** | Agente clasifica la solicitud con categoría que exige aprobación | `PATCH /requests/{id}` con categoría especial | `requestsClient.classifyRequest(...)` |
| **2** | Consultar endpoint de aprobaciones de la solicitud | `GET /requests/{id}/approvals` | `requestsClient.listApprovals(...)` |
| **3** | Validar que exista al menos un registro con estado "PENDING" | Lista de aprobaciones | `expect(approvals[0].status).toBe('PENDING')` |

---

### Resultado Esperado
1. Se autogenera un registro de aprobación en estado `PENDING` vinculado a la solicitud.

---

### Resultado Actual y Evidencias (Para Ejecución Manual)
- **Estado:** [X] Aprobado (Passed)  [ ] Fallido (Failed)  [ ] Bloqueado (Blocked)
- **Fecha de Ejecución:** 2026-09-29
- **Ejecutado por:** Andres Adrian Estrada
- **Enlace a Evidencias / Capturas:** Reporte Playwright HTML / Allure
- **Defecto Asociado:** N/A

---

### Metadatos del Caso de Prueba
- **ID:** `TC-APR-02`
- **Módulo / Funcionalidad:** 5. Aprobaciones / Flujo Estándar sin Aprobación
- **Título:** Categoría "Requiere Aprobación=false" NO dispara el flujo
- **Tipo de Prueba:** Funcional / Positiva
- **Etiquetas:** `@positiva` `@regresiva` `@alta`
- **Prioridad:** Alta
- **Severidad:** Mayor
- **Automatizado:** Sí (Playwright + Node.js)
- **Referencia de Automatización:** `tests/E2E_API/05_aprobaciones.spec.js`
- **Autor:** Andres Adrian Estrada

---

### Precondiciones
1. Categoría estándar con flag `requires_approval: false`.
2. Solicitud clasificada con dicha categoría.

---

### Datos de Prueba (Test Data)
- **Payload Clasificación:** `{"category_id": <catWithoutApprovalId>}`

---

### Pasos de Ejecución (Test Steps)
| Paso # | Acción del Usuario | Datos / Parámetros | Localizador Sugerido |
| :---: | :--- | :--- | :--- |
| **1** | Agente clasifica la solicitud con categoría estándar | `PATCH /requests/{id}` | `requestsClient.classifyRequest(...)` |
| **2** | Consultar endpoint de aprobaciones de la solicitud | `GET /requests/{id}/approvals` | `requestsClient.listApprovals(...)` |
| **3** | Validar que la lista de aprobaciones esté vacía | Array vacío `[]` | `expect(approvals.length).toBe(0)` |

---

### Resultado Esperado
1. La lista de aprobaciones retorna vacía (longitud 0), evitando burocracia innecesaria.

---

### Resultado Actual y Evidencias (Para Ejecución Manual)
- **Estado:** [X] Aprobado (Passed)  [ ] Fallido (Failed)  [ ] Bloqueado (Blocked)
- **Fecha de Ejecución:** 2026-09-29
- **Ejecutado por:** Andres Adrian Estrada
- **Enlace a Evidencias / Capturas:** Reporte Playwright HTML / Allure
- **Defecto Asociado:** N/A

---

### Metadatos del Caso de Prueba
- **ID:** `TC-APR-07`
- **Módulo / Funcionalidad:** 5. Aprobaciones / Trazabilidad y Auditoría de Decisión
- **Título:** Trazabilidad: quién aprobó/rechazó y cuándo
- **Tipo de Prueba:** Funcional / Positiva
- **Etiquetas:** `@positiva` `@regresiva` `@alta`
- **Prioridad:** Alta
- **Severidad:** Crítica
- **Automatizado:** Sí (Playwright + Node.js)
- **Referencia de Automatización:** `tests/E2E_API/05_aprobaciones.spec.js`
- **Autor:** Andres Adrian Estrada

---

### Precondiciones
1. Solicitud con aprobación en estado PENDING generada.
2. Usuario ADMIN autorizado para decidir aprobaciones.

---

### Datos de Prueba (Test Data)
- **Payload Decisión:** `{"status": "APPROVED", "comment": "Aprobación auditada por dirección técnica"}`

---

### Pasos de Ejecución (Test Steps)
| Paso # | Acción del Usuario | Datos / Parámetros | Localizador Sugerido |
| :---: | :--- | :--- | :--- |
| **1** | Administrador decide la aprobación enviando estado APPROVED | `PATCH /requests/{reqId}/approvals/{apprId}` con token Admin | `requestsClient.decideApproval(...)` |
| **2** | Validar que se guarde el email del aprobador y timestamp `decided_at` | Respuesta de aprobación | `expect(decideData.decided_at).not.toBeNull()` |
| **3** | Consultar historial de auditoría de la solicitud | `GET /requests/{reqId}/history` | `requestsClient.listHistory(...)` |
| **4** | Validar que el historial registre el evento de aprobación | Historial no vacío | `expect(history.length).toBeGreaterThan(0)` |

---

### Resultado Esperado
1. La aprobación se actualiza con `status: APPROVED`, fecha `decided_at` y datos del usuario aprobador.
2. El log de auditoría (`/history`) registra el evento completo para trazabilidad regulatoria.

---

### Resultado Actual y Evidencias (Para Ejecución Manual)
- **Estado:** [X] Aprobado (Passed)  [ ] Fallido (Failed)  [ ] Bloqueado (Blocked)
- **Fecha de Ejecución:** 2026-09-29
- **Ejecutado por:** Andres Adrian Estrada
- **Enlace a Evidencias / Capturas:** Reporte Playwright HTML / Allure
- **Defecto Asociado:** N/A

---

### Metadatos del Caso de Prueba
- **ID:** `TC-APR-08`
- **Módulo / Funcionalidad:** 5. Aprobaciones / Prevención de Conflicto de Interés
- **Título:** Customer no puede auto-aprobar su propia solicitud
- **Tipo de Prueba:** Funcional / Negativa
- **Etiquetas:** `@negativa` `@regresiva` `@alta`
- **Prioridad:** Alta
- **Severidad:** Crítica
- **Automatizado:** Sí (Playwright + Node.js)
- **Referencia de Automatización:** `tests/E2E_API/05_aprobaciones.spec.js`
- **Autor:** Andres Adrian Estrada

---

### Precondiciones
1. Solicitud perteneciente a un Customer con aprobación PENDING.
2. Token de dicho Customer disponible.

---

### Datos de Prueba (Test Data)
- **Token:** Bearer Token de Customer solicitante
- **Payload:** `{"status": "APPROVED", "comment": "Intento de auto-aprobación"}`

---

### Pasos de Ejecución (Test Steps)
| Paso # | Acción del Usuario | Datos / Parámetros | Localizador Sugerido |
| :---: | :--- | :--- | :--- |
| **1** | Customer intenta decidir su propia aprobación | `PATCH /requests/{reqId}/approvals/{apprId}` con token de Customer | `requestsClient.decideApproval(...)` |
| **2** | Verificar código de respuesta HTTP | Código HTTP 403 | `expect(res.status()).toBe(403)` |

---

### Resultado Esperado
1. El backend deniega la auto-aprobación con HTTP 403 Forbidden.
2. La aprobación permanece intacta en estado `PENDING`.

---

### Resultado Actual y Evidencias (Para Ejecución Manual)
- **Estado:** [X] Aprobado (Passed)  [ ] Fallido (Failed)  [ ] Bloqueado (Blocked)
- **Fecha de Ejecución:** 2026-09-29
- **Ejecutado por:** Andres Adrian Estrada
- **Enlace a Evidencias / Capturas:** Reporte Playwright HTML / Allure
- **Defecto Asociado:** N/A

---

# Módulo 6: Service Admin

---

### Metadatos del Caso de Prueba
- **ID:** `TC-ADM-12`
- **Módulo / Funcionalidad:** 6. Service Admin / Unicidad e Integridad de Catálogo
- **Título:** Crear entidades duplicadas (nombre repetido) → validación
- **Tipo de Prueba:** Funcional / Negativa
- **Etiquetas:** `@negativa` `@regresiva` `@media`
- **Prioridad:** Media
- **Severidad:** Mayor
- **Automatizado:** Sí (Playwright + Node.js)
- **Referencia de Automatización:** `tests/E2E_API/06_service_admin.spec.js`
- **Autor:** Andres Adrian Estrada

---

### Precondiciones
1. Administrador autenticado con token válido.
2. Registro de categoría y prioridad base creados previamente.

---

### Datos de Prueba (Test Data)
- **Categoría Duplicada:** Mismo nombre ya existente en base de datos
- **Prioridad Duplicada:** Nivel 7 ya existente

---

### Pasos de Ejecución (Test Steps)
| Paso # | Acción del Usuario | Datos / Parámetros | Localizador Sugerido |
| :---: | :--- | :--- | :--- |
| **1** | Admin crea categoría legítima inicial | `POST /categories` con nombre único | `catalogClient.createCategory(...)` |
| **2** | Admin intenta crear una segunda categoría con el mismo nombre | `POST /categories` con nombre repetido | `catalogClient.createCategory(...)` |
| **3** | Validar que el servidor rechace con conflicto de unicidad | Status HTTP 409 y mensaje "Ya existe una categoría" | `expect(dupCat.status()).toBe(409)` |
| **4** | Admin intenta crear prioridad con nivel numérico ya ocupado | `POST /priorities` con `level: 7` | `catalogClient.createPriority(...)` |
| **5** | Validar que el servidor rechace con conflicto | Status HTTP 409 y mensaje de prioridad duplicada | `expect(dupPri.status()).toBe(409)` |

---

### Resultado Esperado
1. Ambas peticiones duplicadas son rechazadas con código HTTP 409 Conflict.
2. No se generan registros redundantes ni inconsistencias en base de datos.

---

### Resultado Actual y Evidencias (Para Ejecución Manual)
- **Estado:** [X] Aprobado (Passed)  [ ] Fallido (Failed)  [ ] Bloqueado (Blocked)
- **Fecha de Ejecución:** 2026-09-29
- **Ejecutado por:** Andres Adrian Estrada
- **Enlace a Evidencias / Capturas:** Reporte Playwright HTML / Allure
- **Defecto Asociado:** N/A

---

# Módulo 7: Seguridad

---

### Metadatos del Caso de Prueba
- **ID:** `TC-SEC-01`
- **Módulo / Funcionalidad:** 7. Seguridad / Aislamiento Estricto IDOR
- **Título:** IDOR: customer no ve solicitudes ajenas
- **Tipo de Prueba:** Funcional / Negativa
- **Etiquetas:** `@negativa` `@regresiva` `@alta`
- **Prioridad:** Alta
- **Severidad:** Crítica
- **Automatizado:** Sí (Playwright + Node.js)
- **Referencia de Automatización:** `tests/E2E_API/07_seguridad.spec.js`
- **Autor:** Andres Adrian Estrada

---

### Precondiciones
1. Solicitud creada legítimamente por Customer A.
2. Customer B con credenciales independientes en la plataforma.

---

### Datos de Prueba (Test Data)
- **Customer A:** Creador legítimo
- **Customer B:** Atacante simulado
- **Endpoint:** `GET /customer/requests/{requestAId}`

---

### Pasos de Ejecución (Test Steps)
| Paso # | Acción del Usuario | Datos / Parámetros | Localizador Sugerido |
| :---: | :--- | :--- | :--- |
| **1** | Customer B envía petición GET al endpoint de cliente con ID de Customer A | Token de Customer B | `GET /customer/requests/{requestAId}` |
| **2** | Inspeccionar respuesta del servidor | Código HTTP 403 Forbidden | `expect([403, 404]).toContain(res.status())` |

---

### Resultado Esperado
1. El sistema bloquea la fuga de datos con HTTP 403 Forbidden.
2. Mensaje indica denegación de acceso por pertenecer a otro usuario.

---

### Resultado Actual y Evidencias (Para Ejecución Manual)
- **Estado:** [X] Aprobado (Passed)  [ ] Fallido (Failed)  [ ] Bloqueado (Blocked)
- **Fecha de Ejecución:** 2026-09-29
- **Ejecutado por:** Andres Adrian Estrada
- **Enlace a Evidencias / Capturas:** Reporte Playwright HTML / Allure
- **Defecto Asociado:** N/A

---

### Metadatos del Caso de Prueba
- **ID:** `TC-SEC-02`
- **Módulo / Funcionalidad:** 7. Seguridad / Protección de Comentarios y Archivos
- **Título:** IDOR: customer no accede a comentarios/archivos ajenos
- **Tipo de Prueba:** Funcional / Negativa
- **Etiquetas:** `@negativa` `@regresiva` `@alta`
- **Prioridad:** Alta
- **Severidad:** Crítica
- **Automatizado:** Sí (Playwright + Node.js)
- **Referencia de Automatización:** `tests/E2E_API/07_seguridad.spec.js`
- **Autor:** Andres Adrian Estrada

---

### Precondiciones
1. Solicitud activa perteneciente exclusivamente a Customer A.

---

### Datos de Prueba (Test Data)
- **Endpoint:** `POST /customer/requests/{requestAId}/comments`
- **Payload:** `{"content": "Intento de comentario no autorizado"}`

---

### Pasos de Ejecución (Test Steps)
| Paso # | Acción del Usuario | Datos / Parámetros | Localizador Sugerido |
| :---: | :--- | :--- | :--- |
| **1** | Customer B intenta inyectar un comentario en solicitud de Customer A | `POST /customer/requests/{requestAId}/comments` | `customerClient.addComment(...)` |
| **2** | Validar código de error | Status HTTP 403 o 404 | `expect([403, 404]).toContain(res.status())` |

---

### Resultado Esperado
1. La API rechaza el intento con HTTP 403/404 sin persistir comentario alguno.

---

### Resultado Actual y Evidencias (Para Ejecución Manual)
- **Estado:** [X] Aprobado (Passed)  [ ] Fallido (Failed)  [ ] Bloqueado (Blocked)
- **Fecha de Ejecución:** 2026-09-29
- **Ejecutado por:** Andres Adrian Estrada
- **Enlace a Evidencias / Capturas:** Reporte Playwright HTML / Allure
- **Defecto Asociado:** N/A

---

### Metadatos del Caso de Prueba
- **ID:** `TC-SEC-03`
- **Módulo / Funcionalidad:** 7. Seguridad / Bypass de Interfaz Gráfica (API-level RBAC)
- **Título:** Bypass de UI: endpoint restringido llamado con rol inferior vía API
- **Tipo de Prueba:** Funcional / Negativa
- **Etiquetas:** `@negativa` `@regresiva` `@alta`
- **Prioridad:** Alta
- **Severidad:** Crítica
- **Automatizado:** Sí (Playwright + Node.js)
- **Referencia de Automatización:** `tests/E2E_API/07_seguridad.spec.js`
- **Autor:** Andres Adrian Estrada

---

### Precondiciones
1. Endpoint `PATCH /requests/{id}` restringido a roles de soporte (Agent y Admin).
2. Usuario con rol inferior (Customer) autenticado.

---

### Datos de Prueba (Test Data)
- **Token:** Bearer Token de Customer A
- **Payload:** `{"category_id": 1}`

---

### Pasos de Ejecución (Test Steps)
| Paso # | Acción del Usuario | Datos / Parámetros | Localizador Sugerido |
| :---: | :--- | :--- | :--- |
| **1** | Customer invoca directamente el endpoint interno `PATCH /requests/{id}` | Token de Customer | `PATCH /requests/{requestAId}` |
| **2** | Validar que el servidor no confíe en la UI y valide a nivel de endpoint | Status HTTP 403 | `expect(res.status()).toBe(403)` |

---

### Resultado Esperado
1. El backend responde con HTTP 403 Forbidden y mensaje de falta de permisos.

---

### Resultado Actual y Evidencias (Para Ejecución Manual)
- **Estado:** [X] Aprobado (Passed)  [ ] Fallido (Failed)  [ ] Bloqueado (Blocked)
- **Fecha de Ejecución:** 2026-09-29
- **Ejecutado por:** Andres Adrian Estrada
- **Enlace a Evidencias / Capturas:** Reporte Playwright HTML / Allure
- **Defecto Asociado:** N/A

---

### Metadatos del Caso de Prueba
- **ID:** `TC-SEC-04`
- **Módulo / Funcionalidad:** 7. Seguridad / Firma Inválida y Secret Forgery
- **Título:** JWT alterado (rol modificado sin re-firmar) → rechazado
- **Tipo de Prueba:** Funcional / Negativa
- **Etiquetas:** `@negativa` `@regresiva` `@alta`
- **Prioridad:** Alta
- **Severidad:** Crítica
- **Automatizado:** Sí (Playwright + Node.js)
- **Referencia de Automatización:** `tests/E2E_API/07_seguridad.spec.js`
- **Autor:** Andres Adrian Estrada

---

### Precondiciones
1. Generador de token firmado con clave espuria (`createInvalidSignedToken()`).

---

### Datos de Prueba (Test Data)
- **Token:** Token con firma HMAC generada con clave inválida (`completely-wrong-key-xyz`)

---

### Pasos de Ejecución (Test Steps)
| Paso # | Acción del Usuario | Datos / Parámetros | Localizador Sugerido |
| :---: | :--- | :--- | :--- |
| **1** | Enviar petición GET `/auth/me` con token que posee firma criptográfica falsa | Header `Authorization: Bearer <fakeToken>` | `authClient.getMe(...)` |
| **2** | Comprobar rechazo inmediato | Status HTTP 401 o 403 | `expect([401, 403]).toContain(res.status())` |

---

### Resultado Esperado
1. El backend detecta la firma forjada y rechaza la conexión con HTTP 401 Unauthorized.

---

### Resultado Actual y Evidencias (Para Ejecución Manual)
- **Estado:** [X] Aprobado (Passed)  [ ] Fallido (Failed)  [ ] Bloqueado (Blocked)
- **Fecha de Ejecución:** 2026-09-29
- **Ejecutado por:** Andres Adrian Estrada
- **Enlace a Evidencias / Capturas:** Reporte Playwright HTML / Allure
- **Defecto Asociado:** N/A

---

### Metadatos del Caso de Prueba
- **ID:** `TC-SEC-05`
- **Módulo / Funcionalidad:** 7. Seguridad / Escalamiento de Privilegios e Inyección de Parámetros
- **Título:** Escalamiento por parámetro oculto ("role":"admin" en creación de usuario)
- **Tipo de Prueba:** Funcional / Negativa
- **Etiquetas:** `@negativa` `@regresiva` `@alta`
- **Prioridad:** Alta
- **Severidad:** Crítica
- **Automatizado:** Sí (Playwright + Node.js)
- **Referencia de Automatización:** `tests/E2E_API/07_seguridad.spec.js`
- **Autor:** Andres Adrian Estrada

---

### Precondiciones
1. Esquema estricto de Pydantic en `POST /users` exigiendo `role_id: int`.

---

### Datos de Prueba (Test Data)
- **Ataque 1:** Inyección de `role: "admin"` desde cuenta de Customer
- **Ataque 2:** Inyección de `role: "admin"` omitiendo `role_id` desde cuenta Admin

---

### Pasos de Ejecución (Test Steps)
| Paso # | Acción del Usuario | Datos / Parámetros | Localizador Sugerido |
| :---: | :--- | :--- | :--- |
| **1** | Customer intenta crear usuario inyectando `"role": "admin"` | `POST /users` con token Customer | `usersClient.createUser(...)` |
| **2** | Validar rechazo por autorización | Status HTTP 403 Forbidden | `expect(unauthRes.status()).toBe(403)` |
| **3** | Admin intenta enviar `"role": "admin"` omitiendo el campo tipado `role_id` | `POST /users` con token Admin y body incompleto | `usersClient.createUser(...)` |
| **4** | Validar que el validador Pydantic rechace parámetro no soportado | Status HTTP 422 Unprocessable Entity | `expect(badParamRes.status()).toBe(422)` |

---

### Resultado Esperado
1. El intento no autorizado es bloqueado con HTTP 403.
2. La inyección de campo sin tipo es rechazada con HTTP 422 exigiendo `role_id`.

---

### Resultado Actual y Evidencias (Para Ejecución Manual)
- **Estado:** [X] Aprobado (Passed)  [ ] Fallido (Failed)  [ ] Bloqueado (Blocked)
- **Fecha de Ejecución:** 2026-09-29
- **Ejecutado por:** Andres Adrian Estrada
- **Enlace a Evidencias / Capturas:** Reporte Playwright HTML / Allure
- **Defecto Asociado:** N/A

---

# Módulo 9: Smoke (Pre-build)

---

### Metadatos del Caso de Prueba
- **ID:** `SM-04`
- **Módulo / Funcionalidad:** 9. Smoke (pre-build) / Disponibilidad Global de la API
- **Título:** Health check: todos los servicios levantan correctamente
- **Tipo de Prueba:** Funcional / Positiva
- **Etiquetas:** `@positiva` `@regresiva` `@alta`
- **Prioridad:** Alta
- **Severidad:** Crítica
- **Automatizado:** Sí (Playwright + Node.js)
- **Referencia de Automatización:** `tests/E2E_API/08_smoke.spec.js`
- **Autor:** Andres Adrian Estrada

---

### Precondiciones
1. Servidor web Uvicorn y base de datos relacional PostgreSQL inicializados.

---

### Datos de Prueba (Test Data)
- **Endpoint:** `GET /health`
- **Payload:** N/A

---

### Pasos de Ejecución (Test Steps)
| Paso # | Acción del Usuario | Datos / Parámetros | Localizador Sugerido |
| :---: | :--- | :--- | :--- |
| **1** | Enviar petición GET al endpoint de verificación de salud del sistema | URL `/health` | `request.get(ENDPOINTS.HEALTH)` |
| **2** | Comprobar código de estado HTTP 200 OK | Código 200 | `expect(res.status()).toBe(200)` |
| **3** | Validar cuerpo de respuesta JSON `{"status": "ok"}` | JSON `{status: 'ok'}` | `expect(body.status).toBe('ok')` |

---

### Resultado Esperado
1. El servicio responde en milisegundos con HTTP 200 y `{"status": "ok"}` garantizando estabilidad pre-despliegue.

---

### Resultado Actual y Evidencias (Para Ejecución Manual)
- **Estado:** [X] Aprobado (Passed)  [ ] Fallido (Failed)  [ ] Bloqueado (Blocked)
- **Fecha de Ejecución:** 2026-09-29
- **Ejecutado por:** Andres Adrian Estrada
- **Enlace a Evidencias / Capturas:** Reporte Playwright HTML / Allure
- **Defecto Asociado:** N/A
