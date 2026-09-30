# 🧪 ServiceFlow — Framework de Automatización de Pruebas API

Framework integral de pruebas automatizadas para la API REST de **ServiceFlow**, desarrollado con **Playwright Test** y **AJV** (validación de esquemas JSON).

> **Responsable de QA:** Andrés Uzeda — QA Engineer  
> **Proyecto:** ServiceFlow (No Country — S08-26-Equipo-20)  
> **Área:** Back-End API Testing & Quality Assurance  

---

## 🛠️ Tecnologías y Herramientas

- **Playwright Test (`@playwright/test`):** Motor de automatización y cliente HTTP asíncrono para pruebas E2E de API.
- **JavaScript (Node.js):** Lenguaje base de desarrollo de las pruebas y utilidades.
- **AJV (`ajv` + `ajv-formats`):** Validador de contratos y esquemas JSON Schema (Draft 7 / 2020-12).
- **Playwright HTML Reporter:** Generador de reportes visuales e interactivos con trazas, tiempos y logs.

---

## 📂 Estructura del Proyecto

```text
PruebasAPI/
├── api/
│   ├── clients/                  # Clientes HTTP por módulo del negocio
│   │   ├── AuthClient.js         # /auth (login, me, cambio de password)
│   │   ├── CatalogClient.js      # /categories, /priorities
│   │   ├── CustomerClient.js     # /customer/requests (portal cliente)
│   │   ├── RequestsClient.js     # /requests (clasificación, estados, SLA, aprobaciones)
│   │   └── UsersClient.js        # /users (gestión de usuarios)
│   └── config/
│       └── apiEndpoints.js       # Centralización de URLs y rutas de la API
├── data/
│   ├── testPayloads.json         # Cargas útiles y payloads estructurados
│   └── testUsers.js              # Usuarios de prueba, roles y generadores de tokens
├── schemas/                      # Esquemas JSON para validación de contratos
│   ├── auth.schema.js
│   ├── catalog.schema.js
│   ├── error.schema.js
│   └── request.schema.js
├── tests/
│   ├── E2E_API/                  # Suites de prueba de extremo a extremo
│   │   ├── 01_autenticacion_sistema.spec.js
│   │   ├── 02_customer_solicitudes.spec.js
│   │   ├── 03_service_agent.spec.js
│   │   ├── 04_sla.spec.js
│   │   ├── 05_aprobaciones.spec.js
│   │   ├── 06_service_admin.spec.js
│   │   ├── 07_seguridad.spec.js
│   │   └── 08_smoke.spec.js
│   └── contract/                 # Pruebas adicionales de contrato
├── utils/
│   ├── apiTeardown.js            # Limpieza y eliminación de datos creados vía API
│   ├── logger.js                 # Formateo visual y trazabilidad en consola
│   └── schemaValidator.js        # Motor de validación AJV
├── package.json
├── playwright.config.js          # Configuración global del runner
└── README.md
```

---

## 📋 Requisitos Previos

1. **Node.js**: Versión 18 o superior instalada.
2. **Servidor Back-End en ejecución**: La API de ServiceFlow debe estar corriendo y escuchando en el puerto configurado (por defecto `http://localhost:8000`).
   - Con Uvicorn:
     ```bash
     uvicorn app.main:app --reload
     ```
   - O con Dock### 1. Ejecutar todas las pruebas
Ejecuta la suite completa de 31 casos de prueba:
```bash
npm test
```
o directamente con el CLI de Playwright:
```bash
npx playwright test
```

### 2. Ejecutar solo la suite E2E
```bash
npm run test:e2e
```

### 3. Ejecutar una suite específica por archivo
Puedes correr de forma individual cualquiera de las suites temáticas:

- **Autenticación y Sistema:**
  ```bash
  npx playwright test tests/E2E_API/01_autenticacion_sistema.spec.js
  ```
- **Portal de Solicitudes del Cliente (Customer):**
  ```bash
  npx playwright test tests/E2E_API/02_customer_solicitudes.spec.js
  ```
- **Flujo de Trabajo del Service Agent:**
  ```bash
  npx playwright test tests/E2E_API/03_service_agent.spec.js
  ```
- **Cálculo y Cumplimiento de SLA:**
  ```bash
  npx playwright test tests/E2E_API/04_sla.spec.js
  ```
- **Flujo de Aprobaciones y Auditoría:**
  ```bash
  npx playwright test tests/E2E_API/05_aprobaciones.spec.js
  ```
- **Administración del Sistema (Service Admin):**
  ```bash
  npx playwright test tests/E2E_API/06_service_admin.spec.js
  ```
- **Seguridad (IDOR, Bypass de Roles, JWT Alterado):**
  ```bash
  npx playwright test tests/E2E_API/07_seguridad.spec.js
  ```
- **Smoke Tests (Pre-build / Health check):**
  ```bash
  npx playwright test tests/E2E_API/08_smoke.spec.js
  ```

### 4. Modo UI / Interactivo
Para depurar y observar cada petición HTTP y respuesta paso a paso en tiempo real:
```bash
npx playwright test --ui
```

---

## 📊 Visualización de Reportes

Al finalizar la ejecución, se generan automáticamente reportes interactivos tanto con **Playwright Reporter** como con **Allure Report**:

### Opción A: Reporte Allure (Dashboard avanzado)
1. **Generar y abrir el dashboard en el navegador:**
   ```bash
   npm run allure:serve
   # o directamente:
   npx allure serve allure-results
   ```
2. **O generar el reporte estático y abrirlo:**
   ```bash
   npm run allure:generate
   npm run allure:open
   ```

### Opción B: Reporte nativo de Playwright
1. **Abrir el reporte HTML:**
   ```bash
   npm run report
   # o
   npx playwright show-report
   ```
2. **Acceso web:**
   Servidor local en 👉 **`http://localhost:9323`** (presiona `Ctrl + C` para detenerlo).


---

## 🧹 Ciclo de Vida: Teardown y Limpieza

### Limpieza de Datos en Base de Datos (Teardown vía API)
Para mantener la base de datos limpia y garantizar la idempotencia de las pruebas:
- El módulo `utils/apiTeardown.js` registra los identificadores de recursos temporales creados durante los tests (usuarios de prueba, categorías, prioridades).
- En el hook `test.afterAll`, se ejecutan llamadas controladas a los endpoints de eliminación (`DELETE /users/{id}`, `DELETE /categories/{id}`, etc.) para revertir las entidades de prueba.

### Limpieza de Artefactos de Ejecución
Para borrar los reportes anteriores, trazas y archivos temporales generados por Playwright:
```bash
npm run clean
```
*(Elimina las carpetas `playwright-report/`, `test-results/` y el archivo `test-results.json`).*

---

## 📑 Matriz de Cobertura de Pruebas (31 Casos)

| ID Caso | Módulo | Descripción |
| :--- | :--- | :--- |
| **TC-AUTH-04** | Autenticación | Verificación de claims y rol correcto en Token Bearer (`/auth/me`). |
| **TC-AUTH-05** | Autenticación | Acceso a endpoint protegido sin token devuelve HTTP 401. |
| **TC-AUTH-06** | Autenticación | Acceso con token expirado es rechazado con HTTP 401 e "Invalid token". |
| **TC-AUTH-07** | Autenticación | Acceso con token manipulado (firma inválida) rechazado con HTTP 401/403. |
| **TC-AUTH-09** | Autenticación | Rol Customer bloqueado de endpoints administrativos con HTTP 403. |
| **TC-AUTH-10** | Autenticación | Rol Service Agent bloqueado de creación de usuarios con HTTP 403. |
| **TC-SYS-01** | Sistema | Validación de campos obligatorios en payloads devuelve HTTP 422. |
| **TC-SYS-02** | Sistema | Manejo de errores no expone stack traces, secretos ni datos de base de datos. |
| **TC-SYS-03** | Sistema | Validación de contratos JSON de Login y Me con AJV. |
| **TC-SYS-04** | Sistema | Verificación del estado del entorno y base de datos con `/health`. |
| **TC-SYS-05** | Sistema | Tiempo de respuesta de la API con usuario válido autenticado (tiempo de espera hasta recibir respuesta). |
| **TC-CUST-05** | Customer | IDOR: Customer B no puede ver detalle de solicitud de Customer A (403/404). |
| **TC-CUST-10** | Customer | Intento de agregar comentario a solicitud ajena es rechazado. |
| **TC-AGENT-09** | Service Agent | Transición a estados inválidos es rechazada con HTTP 400/422. |
| **TC-AGENT-10** | Service Agent | Resolución de solicitud registra timestamp `resolved_at` en formato ISO 8601. |
| **TC-AGENT-12** | Service Agent | Notas internas privadas de agentes no son visibles para usuarios Customer. |
| **TC-SLA-01** | SLA | Cálculo automático de deadlines de respuesta y resolución según prioridad. |
| **TC-SLA-05** | SLA | Registro del tiempo de primera respuesta (`responded_at`) del agente. |
| **TC-SLA-06** | SLA | Registro del tiempo de resolución final (`resolved_at`) en SLA al cerrar. |
| **TC-SLA-07** | SLA | Validación de zonas horarias UTC y booleanos de cumplimiento on-time. |
| **TC-APR-01** | Aprobaciones | Categoría con aprobación requerida dispara automáticamente flujo PENDING. |
| **TC-APR-02** | Aprobaciones | Categoría estándar sin aprobación no genera registros en approvals. |
| **TC-APR-07** | Aprobaciones | Auditoría y trazabilidad completa de quién aprobó, cuándo y registro en historial. |
| **TC-APR-08** | Aprobaciones | Usuario Customer no puede auto-aprobar su propia solicitud (HTTP 403). |
| **TC-ADM-12** | Service Admin | Validación de unicidad: rechazo con HTTP 409 ante nombres o niveles duplicados. |
| **TC-SEC-01** | Seguridad | IDOR estricto: aislamiento de solicitudes entre clientes. |
| **TC-SEC-02** | Seguridad | IDOR: protección de comentarios y archivos adjuntos ajenos. |
| **TC-SEC-03** | Seguridad | Bypass de UI prevenido: endpoint restringido validado a nivel de API (403). |
| **TC-SEC-04** | Seguridad | Token con firma alterada o clave inválida rechazado por el backend. |
| **TC-SEC-05** | Seguridad | Escalamiento de privilegios prevenido (inyección oculta de `"role":"admin"` rechazada). |
| **SM-04** | Smoke | Health check pre-build: verificación de disponibilidad operativa de la API. |


