const categoryResponseSchema = {
  type: 'object',
  required: ['id', 'name', 'requires_approval'],
  properties: {
    id: { type: 'integer' },
    name: { type: 'string', minLength: 1 },
    description: { type: ['string', 'null'] },
    requires_approval: { type: 'boolean' },
  },
  additionalProperties: false,
};

const priorityResponseSchema = {
  type: 'object',
  required: ['id', 'name', 'level'],
  properties: {
    id: { type: 'integer' },
    name: { type: 'string', minLength: 1 },
    level: { type: 'integer' },
  },
  additionalProperties: false,
};

module.exports = {
  categoryResponseSchema,
  priorityResponseSchema,
};
