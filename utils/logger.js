/**
 * Logger detallado para pruebas de API en Playwright
 * Muestra pasos, peticiones HTTP, códigos de estado y detalle completo de errores HTTP
 */
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  dim: '\x1b[2m',
  cyan: '\x1b[36m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  red: '\x1b[31m',
  gray: '\x1b[90m',
  bgRed: '\x1b[41m',
  white: '\x1b[37m',
};

const HTTP_STATUS_NAMES = {
  200: 'OK',
  201: 'CREATED',
  204: 'NO CONTENT',
  400: 'BAD REQUEST',
  401: 'UNAUTHORIZED (No Autenticado)',
  403: 'FORBIDDEN (Acceso Prohibido / RBAC)',
  404: 'NOT FOUND (No Encontrado)',
  409: 'CONFLICT (Conflicto / Duplicado)',
  413: 'PAYLOAD TOO LARGE',
  422: 'UNPROCESSABLE ENTITY (Error de Validación de Esquema)',
  429: 'TOO MANY REQUESTS (Límite Excedido)',
  500: 'INTERNAL SERVER ERROR',
};

class Logger {
  static getTimestamp() {
    return new Date().toISOString().substring(11, 19);
  }

  static testCase(id, title) {
    console.log(`\n${colors.bright}${colors.blue}══════════════════════════════════════════════════════════════════════${colors.reset}`);
    console.log(`${colors.bright}${colors.cyan} [CASO DE PRUEBA: ${id}] ${title}${colors.reset}`);
    console.log(`${colors.bright}${colors.blue}══════════════════════════════════════════════════════════════════════${colors.reset}`);
  }

  static step(stepNumber, description) {
    console.log(`  ${colors.bright}${colors.magenta}➜ [PASO ${stepNumber}]${colors.reset} ${description} ${colors.gray}(${this.getTimestamp()})${colors.reset}`);
  }

  static request(method, endpoint, body = null) {
    const methodColor = method === 'GET' ? colors.cyan : method === 'POST' ? colors.green : method === 'PATCH' || method === 'PUT' ? colors.yellow : colors.red;
    console.log(`    ${colors.gray}[REQUEST]${colors.reset} ${methodColor}${method}${colors.reset} ${endpoint}`);
    if (body) {
      const formatted = typeof body === 'object' ? JSON.stringify(body) : String(body);
      console.log(`      ${colors.dim}Body: ${formatted.length > 200 ? formatted.substring(0, 197) + '...' : formatted}${colors.reset}`);
    }
  }

  /**
   * Registra la respuesta HTTP con detalle del código de error si status >= 400
   */
  static response(status, body = null, statusText = '') {
    const statusName = HTTP_STATUS_NAMES[status] || statusText || '';

    if (status >= 400) {
      console.log(`    ${colors.bright}${colors.red}  [CÓDIGO DE ERROR HTTP]: ${status} ${statusName}${colors.reset}`);
      if (body) {
        const detail = body.detail !== undefined ? body.detail : body;
        console.log(`       ${colors.yellow} Detalle del Error devuelto por la API:${colors.reset}`);
        if (typeof detail === 'object') {
          console.log(`       ${colors.dim}${JSON.stringify(detail, null, 2).replace(/\n/g, '\n       ')}${colors.reset}`);
        } else {
          console.log(`       ${colors.dim}"${detail}"${colors.reset}`);
        }
      }
    } else {
      console.log(`    ${colors.green} [HTTP STATUS]: ${status} ${statusName}${colors.reset}`);
      if (body) {
        const formatted = typeof body === 'object' ? JSON.stringify(body) : String(body);
        if (formatted.length <= 150) {
          console.log(`       ${colors.dim}↳ Payload: ${formatted}${colors.reset}`);
        } else {
          console.log(`       ${colors.dim}↳ Payload: ${formatted.substring(0, 147)}...${colors.reset}`);
        }
      }
    }
  }

  /**
   * Helper asíncrono para inspeccionar automáticamente un APIResponse de Playwright
   * @param {import('@playwright/test').APIResponse} res
   */
  static async logResponse(res) {
    const status = res.status();
    const statusText = res.statusText();
    let body = null;
    try {
      body = await res.json();
    } catch {
      try {
        const text = await res.text();
        body = text.trim() ? text : null;
      } catch {
        body = null;
      }
    }
    this.response(status, body, statusText);
    return body;
  }

  static pass(message) {
    console.log(`    ${colors.green}✔ ${message}${colors.reset}`);
  }

  static info(message) {
    console.log(`    ${colors.cyan}ℹ ${message}${colors.reset}`);
  }

  static teardown(action, details = '') {
    console.log(`  ${colors.yellow}[TEARDOWN]${colors.reset} ${action} ${colors.gray}${details}${colors.reset}`);
  }

  static error(message, err = null) {
    console.log(`    ${colors.bright}${colors.red}✖ [FALLO]: ${message}${colors.reset}`);
    if (err) {
      console.log(`      ${colors.red}${err.message || err}${colors.reset}`);
    }
  }
}

module.exports = Logger;
