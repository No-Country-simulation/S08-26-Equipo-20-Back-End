const errorResponseSchema = {
  type: 'object',
  required: ['detail'],
  properties: {
    detail: {
      anyOf: [
        { type: 'string' },
        {
          type: 'array',
          items: {
            type: 'object',
            required: ['loc', 'msg', 'type'],
            properties: {
              loc: { type: 'array' },
              msg: { type: 'string' },
              type: { type: 'string' },
            },
          },
        },
      ],
    },
  },
  additionalProperties: true,
};

module.exports = {
  errorResponseSchema,
};
