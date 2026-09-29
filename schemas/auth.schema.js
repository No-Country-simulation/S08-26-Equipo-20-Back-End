const loginResponseSchema = {
  type: 'object',
  required: ['access_token', 'token_type'],
  properties: {
    access_token: { type: 'string', minLength: 10 },
    token_type: { type: 'string', const: 'bearer' },
  },
  additionalProperties: false,
};

const userMeResponseSchema = {
  type: 'object',
  required: ['id', 'name', 'email', 'role', 'role_id', 'is_active', 'must_change_password', 'created_at', 'updated_at'],
  properties: {
    id: { type: 'integer' },
    name: { type: 'string', minLength: 1 },
    email: { type: 'string', format: 'email' },
    role: { type: 'string', enum: ['ADMIN', 'AGENT', 'USER'] },
    team: { type: ['string', 'null'] },
    role_id: { type: 'integer' },
    team_id: { type: ['integer', 'null'] },
    is_active: { type: 'boolean' },
    must_change_password: { type: 'boolean' },
    created_at: { type: 'string' },
    updated_at: { type: 'string' },
  },
  additionalProperties: false,
};

module.exports = {
  loginResponseSchema,
  userMeResponseSchema,
};
