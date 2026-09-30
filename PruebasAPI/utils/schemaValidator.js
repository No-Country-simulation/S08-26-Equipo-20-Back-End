const Ajv = require('ajv');
const addFormats = require('ajv-formats');
const Logger = require('./logger');

const ajv = new Ajv({
  allErrors: true,
  coerceTypes: false,
  strict: false,
});
addFormats(ajv);

function validateSchema(schema, data, schemaName = 'Schema') {
  const validate = ajv.compile(schema);
  const valid = validate(data);

  if (!valid) {
    const errorDetails = validate.errors.map(
      (err) => `Campo '${err.instancePath}': ${err.message} (${JSON.stringify(err.params)})`
    );
    Logger.error(`Fallo en validación de contrato [${schemaName}]`, errorDetails.join('; '));
    return {
      valid: false,
      errors: validate.errors,
      details: errorDetails,
    };
  }

  Logger.pass(`Contrato [${schemaName}] validado correctamente con AJV`);
  return {
    valid: true,
    errors: null,
    details: [],
  };
}

module.exports = {
  ajv,
  validateSchema,
};
